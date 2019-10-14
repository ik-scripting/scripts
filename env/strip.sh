#!/usr/bin/env bash

## strip newlines of envs
# used some code from http://stackoverflow.com/a/11746174

string=`printenv`

arr=()
while read -r line; do
 arr+=("$line")
   if [ -n "$line" ]; then
     declare $line
     #export env with no newline
   fi
done <<< "$string"

#run command following after env-strip.sh
$@
