#!/usr/bin/env bash

function fingerprintBuild {
  if [ "$APP_CENTER_CURRENT_PLATFORM" == "android" ]
  then
    approov registration -add "$APPCENTER_OUTPUT_DIRECTORY/app-release.apk"
  else
    approov registration -add "$APPCENTER_OUTPUT_DIRECTORY/H&B.ipa"
  fi
}

function fingerprintBuildStaging {
  BUILD_EXPIRY="30d"
  if [ "$APP_CENTER_CURRENT_PLATFORM" == "android" ]
  then
    approov registration -add "$APPCENTER_OUTPUT_DIRECTORY/app-release.apk" -expireAfter $BUILD_EXPIRY
  else
    approov registration -add "$APPCENTER_OUTPUT_DIRECTORY/H&B.ipa" -expireAfter $BUILD_EXPIRY
  fi
}

if [ "$AGENT_JOBSTATUS" == "Succeeded" ]; then
  if [ "$BUILD_ENVIRONMENT" == "staging" ]; then
    fingerprintBuildStaging
  else
    fingerprintBuild
  fi
fi
