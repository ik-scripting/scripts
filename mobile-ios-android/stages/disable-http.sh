#!/bin/bash

print_header "Disabling http in favour of https"

# Disable http on Android
echo "Disabling for android"
replace_in_file "s/android:usesCleartextTraffic=\"true\"/android:usesCleartextTraffic=\"false\"/" "android/app/src/main/AndroidManifest.xml"

# Disable http on iOS
echo "Disabling for iOS"
# Replace the relevant keys
if $IS_MAC
then
  sed -i '' '/<key>NSAllowsArbitraryLoads</{n;s/true/false/;}' ./ios/hbapp/Info.plist
  sed -i '' '/<key>NSExceptionAllowsInsecureHTTPLoads</{n;s/true/false/;}' ./ios/hbapp/Info.plist
else
  sed -i '/<key>NSAllowsArbitraryLoads</{n;s/true/false/;}' ./ios/hbapp/Info.plist
  sed -i '/<key>NSExceptionAllowsInsecureHTTPLoads</{n;s/true/false/;}' ./ios/hbapp/Info.plist
fi

print_footer
