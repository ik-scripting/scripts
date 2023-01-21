#!/usr/bin/env bash

printf "Creating build number for build...\n"
VERSION_CODE=$((VERSION_CODE_OFFSET + APPCENTER_BUILD_ID))

if [ "$APP_CENTER_CURRENT_PLATFORM" == "ios" ];
then
  PLIST_PATH="$APPCENTER_SOURCE_DIRECTORY/ios/hbapp/Info.plist"
  printf "Using build number %s for ios\n" "$VERSION_CODE"
  plutil -replace CFBundleVersion -string "$VERSION_CODE" "$PLIST_PATH"
  printf "Done adding build version to ios\n"
fi

if [ "$APP_CENTER_CURRENT_PLATFORM" == "android" ];
then
  printf "Using build number %s for android\n" "$VERSION_CODE"
  GRADLE_PATH="$APPCENTER_SOURCE_DIRECTORY/android/app/build.gradle"
  sed -i "" "s/versionCode [0-9]*/versionCode $VERSION_CODE/" "$GRADLE_PATH"
  printf "Done adding build version to android\n"
fi
