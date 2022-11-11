#!/bin/bash
# https://dev.to/emilienmottet/a-journey-into-the-depths-of-gitlab-ci-15j5

# make sure the subtrees is up to date, just add a hook to the post-commit..

subtree_push(){
    git subtree push -P "$1" git@github.com:Name/exercism-"$1"-sol.git master
}

for dir in */; do
    subtree_push "$( basename "$dir" )" 2> /dev/null &
done


for dir in */; do
    wait
done &
