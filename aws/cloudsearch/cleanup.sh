#!/bin/bash

set -e

export CS_DOMAIN=https://yoursearchdomain.yourregion.cloudsearch.amazonaws.com

# Get ids of all existing documents, reformat as
# [{ type: "delete", id: "ID" }, ...] using jq
aws cloudsearchdomain search \
  --endpoint-url=$CS_DOMAIN \
  --size=10000 \
  --query-parser=structured \
  --search-query="matchall" \
  | jq '[.hits.hit[] | {type: "delete", id: .id}]' \
  > delete-all.json

# Delete the documents
aws cloudsearchdomain upload-documents \
  --endpoint-url=$CS_DOMAIN \
  --content-type='application/json' \
  --documents=delete-all.json
