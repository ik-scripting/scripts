#!/bin/bash

print_header "Copying Airship configuration"

# Pick the correct config for each platform
case "$ENVIRONMENT" in
 $PRODUCTION)
  ANDROID_CONFIG_SOURCE="$CONFIG_DIR_PATH/airship/android/production.properties"
  IOS_CONFIG_SOURCE="$CONFIG_DIR_PATH/airship/ios/production.plist" ;;
 $STAGING)
  ANDROID_CONFIG_SOURCE="$CONFIG_DIR_PATH/airship/android/staging.properties"
  IOS_CONFIG_SOURCE="$CONFIG_DIR_PATH/airship/ios/staging.plist" ;;
esac

echo "Using config at $ANDROID_CONFIG_SOURCE for Android"
echo "Using config at $IOS_CONFIG_SOURCE for iOS"

# Copy the selected configs to the correct destinations
cp $ANDROID_CONFIG_SOURCE android/app/src/main/assets/airshipconfig.properties
cp $IOS_CONFIG_SOURCE ios/AirshipConfig.plist

print_footer
