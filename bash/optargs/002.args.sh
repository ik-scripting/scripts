#!/bin/bash

set -euo pipefail

APPLICATION=
usage() { echo "Usage: $0 [-e <dev|qa>] [-p <api|image-review>]" 1>&2; exit 1; }

while getopts ":e:a:" option; do
  case $option in
    e) export ENVIRONMENT="$OPTARG";;
    a) APPLICATION="$OPTARG $APPLICATION";;
		*) usage;;
  esac
done

: $ENVIRONMENT
: $APPLICATION