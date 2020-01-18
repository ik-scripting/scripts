#!/bin/bash

loggroup=$1
dryrun=$2

if [[ -z $loggroup || $loggroup == '--dryrun' ]]; then
  echo "Usage: $0 LogGroup [--dryrun]"
  exit 1
fi

while [[ -z $next_token || $next_token != "" ]]; do
  if [[ $next_token != "" ]]; then
    starting_token="--starting-token $next_token"
  fi
  result=$(aws --output text logs describe-log-streams --log-group-name $loggroup --max-items 100 $starting_token)
  next_token=$(echo "$result" | grep NEXTTOKEN | awk '{print $2}')
  empty_streams=$(echo "$result" | grep LOGSTREAMS | awk '{if ($8 < 1) print $7}')

  for stream in $empty_streams; do
    if [ ! -z $dryrun ]; then
      echo "aws logs delete-log-stream --log-group-name $loggroup --log-stream-name $stream"
    else
      aws logs delete-log-stream --log-group-name $loggroup --log-stream-name $stream
      if [ $? -eq 0 ]; then
        echo "Deleted $stream"
      else
        echo "Failed to delete $stream"
      fi
      sleep 0.1
    fi
    sleep 0.5
  done
done
