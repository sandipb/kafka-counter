#!/usr/bin/env python3
from ensurepip import bootstrap
import sys
import argparse
import logging
import signal
import json
import time
from typing import List, Dict, Union
from collections import defaultdict

import yaml
from jsonpath_ng import parse as json_parse
from kafka import KafkaConsumer

DEFAULT_UPDATE_MS = 1000

def err_exit(*msg):
    logging.critical(*msg)
    sys.exit(1)

class EventCounter(object):
    def __init__(self, topics: Dict[str, str], update_every=DEFAULT_UPDATE_MS):
        self.counts = {}
        self.total = 0
        self.ttotals = defaultdict(int)
        self.topics = topics
        self.update_every = update_every
        self.last_update = time.time()
        for topic in topics:
            self.counts[topic] = defaultdict(int)
    
    def add(self, topic: str, val: str):
        if topic not in self.counts:
            logging.warning("Invalid topic added to counter: %s", topic)
        self.counts[topic][val] += 1
        self.total += 1
        self.ttotals[topic] += 1
        self.display()
    
    def display(self):
        if self.last_update != 0 and ((time.time()-self.last_update)*1000 < self.update_every):
            return
        texts = []
        for topic in sorted(self.counts.keys()):
            if not self.ttotals[topic]:
                continue
            val_text = ", ".join([
                f"{val}={self.counts[topic][val]}({self.counts[topic][val]/self.ttotals[topic]*100:2.1f}%)"
                for val in sorted(self.counts[topic].keys(), key=lambda x: self.counts[topic][x], reverse=True)
            ])
            texts.append(f"{self.topics[topic]:15}[{self.ttotals[topic]:6}]({val_text})")
        sys.stdout.write("\033c")
        sys.stdout.write("\n".join(texts) + "\n")
        self.last_update = time.time()
        # sys.stdout.flush()

    def stats(self):
        print(f"Total events received: {self.total}")
        for topic in sorted(self.counts.keys(), key=lambda x: self.ttotals[x], reverse=True):
            if self.ttotals[topic]:
                print(f"\t{self.topics[topic]:30}: {self.ttotals[topic]} ({self.ttotals[topic]/self.total*100:2.1f}%)")

def load_config(path: str) -> any:
    try:
        logging.debug("Reading config from: %s", path)
        with open(path) as f:
            data = yaml.safe_load(f)
    except Exception as e:
        err_exit("Could not read config file: %s", e)

    d = json_parse('$.common.broker').find(data)

    if not d or type(d[0].value) != str:
        err_exit("'broker' key with string required in config")
    logging.debug("Broker=%s", d[0].value)

    if 'count' not in data or type(data["count"]) != dict:
        err_exit("'count' key missing or not a list in config")

    for topic, entry in data["count"].items():
        if 'name' not in entry:
            entry['name'] = topic
        if entry.get("countOnly", False):
            continue
        if 'path' not in entry or type(entry['path']) != str:
            err_exit("'path' key missing or not an str for topic %s", topic)
        try:
            entry['path_expr'] = json_parse(entry['path'])
        except Exception as e:
            err_exit("Invalid json path for topic %s: %s", topic, e)
    return data

def setup() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", "-d", action="store_true", help="Run in debug mode")
    parser.add_argument("--config", "-c", required=True, help="Yaml config file")
    parser.add_argument("--update-every", "-u", default=500, help="How many ms between display updates")
    args = parser.parse_args()

    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level,format="%(asctime)-15s [%(levelname)s] %(message)s", datefmt='%Y-%m-%d %H:%M:%S')
    logging.getLogger('kafka').setLevel(logging.WARN)
    return args

def listen_to_kafka(config: dict, counter: EventCounter):
    consumer = KafkaConsumer(
        bootstrap_servers=config["common"]["broker"],
        client_id="kafka-count",
        value_deserializer=json.loads,
        request_timeout_ms = 1000*10,
        enable_auto_commit=False,
        )
    count_cfg = config["count"]

    topics = count_cfg.keys()
    consumer.subscribe(topics)
    for msg in consumer:
        mtopic = msg.topic
        if mtopic not in topics:
            continue
        topic_cfg = count_cfg[mtopic]
        if topic_cfg.get("countOnly", False):
            counter.add(mtopic, "COUNT")
        else:
            val = topic_cfg["path_expr"].find(msg.value)
            if val:
                logging.debug(f"topic={mtopic}, key={val[0].value}")
                counter.add(mtopic, val[0].value)
            else:
                # logging.warning("Message from topic '%s' doesn't have value for path: %s", mtopic, topic_cfg["path"])
                counter.add(mtopic, "_MALFORMED")


def sig_quit_clean(counter: EventCounter):
    def quit(sig, frame):
        sys.stdout.write("\n")
        # logging.info("Interrupted. Exiting.")
        counter.stats()
        sys.exit(1)
    signal.signal(signal.SIGINT, quit)

def main():
    args = setup()
    config = load_config(args.config)
    counter = EventCounter({
        topic_name: config["count"][topic_name]["name"]
        for topic_name in config["count"].keys()
    }, update_every=args.update_every)
    sig_quit_clean(counter)
    listen_to_kafka(config, counter)

if __name__ == "__main__":
    main()
