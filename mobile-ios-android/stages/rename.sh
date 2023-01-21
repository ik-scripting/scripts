#!/bin/bash

print_header "Performing rename tasks"

# Pick the correct bundle id
case "$ENVIRONMENT" in
 "$PRODUCTION")
  BUNDLE_ID_IOS=$BUNDLE_ID_PRODUCTION_IOS
  BUNDLE_ID_ANDROID=$BUNDLE_ID_PRODUCTION_ANDROID
  BUNDLE_ID_RAW_ANDROID=$BUNDLE_ID_RAW_PRODUCTION_ANDROID ;;
 "$STAGING")
  BUNDLE_ID_IOS=$BUNDLE_ID_STAGING_IOS
  BUNDLE_ID_ANDROID=$BUNDLE_ID_STAGING_ANDROID
  BUNDLE_ID_RAW_ANDROID=$BUNDLE_ID_RAW_STAGING_ANDROID ;;
esac

echo "Using $BUNDLE_ID_IOS for ios"
echo "Using $BUNDLE_ID_ANDROID for android"

# Rename as much as possible automatically
# npx react-native-ci-tools bundle "$BUNDLE_ID_IOS" "H&B" -i
npx react-native-ci-tools bundle "$BUNDLE_ID_ANDROID" "H&B" -a

# Manually rename missed items
echo "Manually renaming remaining files..."

### iOS items
replace_in_file "s/$BUNDLE_ID_IOS/$BUNDLE_ID_IOS.NotificationServiceExtension/" ios/NotificationServiceExtension/Info.plist
replace_in_file "s/$BUNDLE_ID_IOS/$BUNDLE_ID_IOS.NotificationContentExtension/" ios/NotificationContentExtension/Info.plist
replace_in_file "s/$BUNDLE_ID_LOCAL_IOS/$BUNDLE_ID_IOS/" "ios/hbapp/Info.plist"
replace_in_file "s/$BUNDLE_ID_LOCAL_IOS/$BUNDLE_ID_IOS/" "ios/hbapp.xcodeproj/project.pbxproj"

#### Android items

declare -a REPLACE_DIRECTORIES_ANDROID=(
  "android/app/src/androidTest/java/com"
  "android/app/src/debug/java/com"
  "android/app/src/main/java/com"
)

for DIR_NAME in "${REPLACE_DIRECTORIES_ANDROID[@]}"
do
  echo "Replacing directory package name for $DIR_NAME"
  mv "$DIR_NAME/$BUNDLE_ID_RAW_LOCAL_ANDROID" "$DIR_NAME/$BUNDLE_ID_RAW_ANDROID"
done

REPLACE_FILES_ANDROID=$(
  ls -R android/app/src |
  awk '/:$/&&f{s=$0;f=0}/:$/&&!f{sub(/:$/,"");s=$0;f=1;next}NF&&f{ print s"/"$0 }' |
  grep "\.\(java\|kt\)$"
)

REPLACE_FILES_ANDROID=( $REPLACE_FILES_ANDROID "android/app/build.gradle" )

for FILE_NAME in "${REPLACE_FILES_ANDROID[@]}"
do
  echo "Replacing $BUNDLE_ID_LOCAL_ANDROID in file $FILE_NAME with $BUNDLE_ID_ANDROID"
  replace_in_file "s/$BUNDLE_ID_LOCAL_ANDROID/$BUNDLE_ID_ANDROID/" "$FILE_NAME"
done

print_footer
