#!/bin/bash

# get the tag of the newest image in a particular repo.

usage() { echo "Usage: $0 [-e <dev|qa>] [-p <api|image-review>]" 1>&2; exit 1; }

while getopts ":r:" option; do
  case $option in
    r) export repository="$OPTARG";;
		*) usage;;
  esac
done

aws ecr describe-images --repository-name $repository \
  --query 'sort_by(imageDetails,& imagePushedAt)[-1].imageTags[0]' --output text