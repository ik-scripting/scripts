#!/bin/bash

set -e

while true; do dig "some-dns.com" | grep time; sleep 2; done
