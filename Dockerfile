FROM python:3.9-alpine3.16
ARG kafka_counter_version=0.0.2
WORKDIR /app
COPY . .
RUN apk add --update --no-cache --virtual .tmp-build-deps gcc g++ libc-dev musl-dev 
RUN apk add  --update --no-cache snappy-dev
RUN python3 -m pip install kafka-counter==0.0.2
RUN apk del .tmp-build-deps


ENTRYPOINT [ "/usr/local/bin/kafka-count" ]