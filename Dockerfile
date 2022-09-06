FROM python:3.9-alpine3.16
ARG kafka_counter_version=0.0.2

# The following will be removed later
RUN apk add --update --no-cache --virtual .tmp-build-deps gcc g++ libc-dev musl-dev 

# This will be needed permanently
RUN apk add  --update --no-cache snappy-dev

RUN python3 -m pip install kafka-counter==0.0.2

# cleanup
RUN apk del .tmp-build-deps

RUN set -xe \
	&& addgroup --gid 2000 app \
	&& adduser --uid 2000 --disabled-password -h /app --ingroup app app

WORKDIR /app

USER app

ENTRYPOINT [ "/usr/local/bin/kafka-count" ]