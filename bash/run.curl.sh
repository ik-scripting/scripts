#!/bin/bash

echo "Show only hosts and redirect route"
curl -v -L host 2>&1 | egrep "^> (Host:|GET)"

echo "List Hosts on redirects"
curl -v -iL https://google.com 2>&1 | egrep "^> (Host:|GET)"