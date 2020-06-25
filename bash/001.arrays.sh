#!/bin/bash

declare -a array=(
  "one"
  "two"
  "three"
  "four"
  "five"
)

# # get length of an array
arraylength=${#array[@]}

for (( i=1; i<${arraylength}+1; i++ ));
do
  publish_artifact ${i} ${arraylength} ${array[$i-1]}
done
