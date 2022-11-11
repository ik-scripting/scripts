#!/bin/bash
# https://dev.to/emilienmottet/a-journey-into-the-depths-of-gitlab-ci-15j5

# For the management of modified files, it is possible to recalculate the modified files using a pre-step.
if [ "$CI_PIPELINE_TRIGGERED" = "true" ]; then
  DIR_TO_BE_TESTED=$(ls -d */)
else
  DIR_TO_BE_TESTED=$(git diff --name-only $CI_COMMIT_SHA^ $CI_COMMIT_SHA */ | cut -d'/' -f1 | sort | uniq)
  if [ -z $DIR_TO_BE_TESTED ]; then
    DIR_TO_BE_TESTED=$(ls -d */)
  fi
fi

# - echo DIR_TO_BE_TESTED=$DIR_TO_BE_TESTED >> build.env
# - cat build.env
