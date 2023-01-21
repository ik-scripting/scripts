#!/bin/bash

print_header "Copying Appcenter configuration"

# Pick the correct config for each platform
case "$ENVIRONMENT" in
 "$PRODUCTION")
  ANDROID_CONFIG_SOURCE="$CONFIG_DIR_PATH/appcenter/android/production.json"
  IOS_CONFIG_SOURCE="$CONFIG_DIR_PATH/appcenter/ios/production.plist" ;;
 "$STAGING")
  ANDROID_CONFIG_SOURCE="$CONFIG_DIR_PATH/appcenter/android/staging.json"
  IOS_CONFIG_SOURCE="$CONFIG_DIR_PATH/appcenter/ios/staging.plist" ;;
esac

echo "Using config at $ANDROID_CONFIG_SOURCE for Android"
echo "Using config at $IOS_CONFIG_SOURCE for iOS"

# Copy the selected configs to the correct destinations
cp "$ANDROID_CONFIG_SOURCE" android/app/src/main/assets/appcenter-config.json
cp "$IOS_CONFIG_SOURCE" ios/hbapp/AppCenter-Config.plist

print_footer
