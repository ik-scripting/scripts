#!/bin/bash

docker run --rm -it -p 8090:8080 --entrypoint /bin/sh --name magnolia --label com.datadoghq.tags.version="0.24.0" k8s.gcr.io/external-dns/external-dns:v0.9.0

docker run --rm -it --entrypoint /bin/sh dwdraju/alpine-curl-jq

docker run -it --rm --entrypoint /bin/sh -v $(pwd)/testdata:/opt/mount/ amaysim/serverless:2.72.1
