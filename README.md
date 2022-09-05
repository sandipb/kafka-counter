# kafka-counter

Count kafka events from multiple topics.

This small utility reads kafka messages from multiple topics and provides you a
running count of the number of seen events. If the message is a json document,
you can also break down the counts for a topic by a specific key indicated by a
JSON path.

When you quit the program pressing Ctrl-C, it also provides some statistics of
the events seen broken down by topics.

## Usage

```console
$ ./kafka-count.py -h
usage: kafka-count.py [-h] [--debug] --config CONFIG [--update-every UPDATE_EVERY]

optional arguments:
  -h, --help            show this help message and exit
  --debug, -d           Run in debug mode
  --config CONFIG, -c CONFIG
                        Yaml config file
  --update-every UPDATE_EVERY, -u UPDATE_EVERY
                        How many ms between display updates
```

## Example config

```yaml
common:
  broker: kafka.default.svc.cluster.local:9092

count:

  k8sNginxIngressLogRaw:
    name: ingress            # Use this name to refer to this topic
    path: kubernetes_cluster # break down the numbers by the string value at this jsonpath location

  k8sNginxModSecurityLogRaw:
    name: modsec
    countOnly: True # Only count the total events
```

## Example Usage

```console
$ kafka-count -c config.yaml
k8sevents      [  1170](cluster1=599(51.2%), cluster2=545(46.6%), cluster3=12(1.0%), cluster4=7(0.6%), cluster5=7(0.6%))
ingress        [ 48878](cluster1=27319(55.9%), cluster2=15953(32.6%), cluster4=3996(8.2%), cluster3=1056(2.2%), cluster5=554(1.1%))
modsec         [     2](COUNT=2(100.0%))
containerd     [ 31054](cluster2=14772(47.6%), cluster1=12291(39.6%), cluster4=1453(4.7%), cluster5=1408(4.5%), cluster3=1130(3.6%))
systemd        [ 10789](cluster2=4731(43.9%), cluster1=3605(33.4%), cluster4=856(7.9%), cluster3=841(7.8%), cluster5=756(7.0%))
^C
Total events received: 93293
	ingress                       : 49945 (53.5%)
	containerd                    : 31276 (33.5%)
	systemd                       : 10894 (11.7%)
	k8sevents                     : 1176 (1.3%)
	modsec                        : 2 (0.0%)
```
