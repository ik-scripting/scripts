#!/usr/bin/env bash

# On my Gitlab CI/CD pipeline, is there a way I can get a list of the changed files?

git diff --name-only origin/$CI_MERGE_REQUEST_SOURCE_BRANCH_NAME origin/$CI_MERGE_REQUEST_TARGET_BRANCH_NAME | grep ".*/${ENV}/.*/*.tfvars"

