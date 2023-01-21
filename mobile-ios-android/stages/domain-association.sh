#!/bin/bash

print_header "Setting up domain association"

# Pick the correct domain for each env
case "$ENVIRONMENT" in
 "$PRODUCTION")
  ASSOC_DOMAIN="www.hollandandbarrett.com" ;;
 "$STAGING")
  ASSOC_DOMAIN="preprod-com.hollandandbarrett.net" ;;
esac

replace_in_file "s/preprod-com.hollandandbarrett.net/$ASSOC_DOMAIN/" "ios/hbapp/H&B.entitlements"
replace_in_file "s/preprod-com.hollandandbarrett.net/$ASSOC_DOMAIN/" "android/app/src/main/AndroidManifest.xml"

print_footer
