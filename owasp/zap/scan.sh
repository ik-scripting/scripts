#!/usr/bin/env bash
# https://www.zaproxy.org/docs/docker/about

WEBSITE_URL="https://google.com"

docker run -i owasp/zap2docker-stable zap-cli quick-scan --self-contained \
  --start-options '-config api.disablekey=true' $WEBSITE_URL