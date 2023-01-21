#!/bin/bash

print_header "Copying Firebase configuration"

# Pick the correct config for each platform
case "$ENVIRONMENT" in
 $PRODUCTION)
  ANDROID_CONFIG_SOURCE="$CONFIG_DIR_PATH/firebase/android/production.json"
  IOS_CONFIG_SOURCE="$CONFIG_DIR_PATH/firebase/ios/production.plist" ;;
 $STAGING)
  ANDROID_CONFIG_SOURCE="$CONFIG_DIR_PATH/firebase/android/staging.json"
  IOS_CONFIG_SOURCE="$CONFIG_DIR_PATH/firebase/ios/staging.plist" ;;
esac

echo "Using config at $ANDROID_CONFIG_SOURCE for Android"
echo "Using config at $IOS_CONFIG_SOURCE for iOS"

# Copy the selected configs to the correct destinations
cp $ANDROID_CONFIG_SOURCE android/app/google-services.json
cp $IOS_CONFIG_SOURCE ios/hbapp/GoogleService-Info.plist
cp $IOS_CONFIG_SOURCE ios/GoogleService-Info.plist

print_footer
