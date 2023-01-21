#!/usr/bin/env bash

function obfuscateIOS {
  IXGUARD_PACKAGE="iXGuard_4_2_3.pkg"
  PKG_PATH="obfuscation/ios/$IXGUARD_PACKAGE"
  LICENSE_PATH="obfuscation/ios/$IXGUARD_PACKAGE"
  IPA_PATH="$APPCENTER_OUTPUT_DIRECTORY/H&B.ipa"

  # Generate license file
  echo "$IXGUARD_LICENSE" | base64 --decode > "$LICENSE_PATH"
  # Install iXGuard package
  installer -pkg "$PKG_PATH" -target CurrentUserHomeDirectory
  # Obfucate the IPA
  ixguard -config obfuscation/ios/ixguard.yml -o "$IPA_PATH" "$IPA_PATH"
}

function obfuscate {
  if [ "$APP_CENTER_CURRENT_PLATFORM" == "ios" ]
  then
    obfuscateIOS
  else
    echo "TODO: Obfuscate android"
  fi
}

if [ "$AGENT_JOBSTATUS" == "Succeeded" ]; then
  obfuscate
fi
