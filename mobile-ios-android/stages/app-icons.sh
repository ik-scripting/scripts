#!/bin/bash

print_header "Adding app icons"

# Pick the correct icon sets for each platform
case "$ENVIRONMENT" in
 $PRODUCTION)
  ANDROID_ICON_PACK_LOCATION="assets/images/icon/ic_launcher/res"
  IOS_ICON_PACK_LOCATION="assets/images/icon/AppIcons/Assets.xcassets/AppIcon.appiconset/." ;;
 $STAGING)
  ANDROID_ICON_PACK_LOCATION="assets/images/staging-icon/ic_launcher/res"
  IOS_ICON_PACK_LOCATION="assets/images/staging-icon/AppIcons/Assets.xcassets/AppIcon.appiconset/." ;;
esac

# Where the icons need to be copied to
ANDROID_ICON_PACK_DESTINATION="android/app/src/main/res"
IOS_ICON_PACK_DESTINATION="ios/hbapp/Images.xcassets/AppIcon.appiconset/"

# All android resolution sets
declare -a ANDROID_RESOLUTIONS=(
  "mipmap-hdpi"
  "mipmap-mdpi"
  "mipmap-xhdpi"
  "mipmap-xxhdpi"
  "mipmap-xxxhdpi"
)

# Copy android icons
echo "Copying android icons"
echo "Using icons at $ANDROID_ICON_PACK_LOCATION"
for resolution in "${ANDROID_RESOLUTIONS[@]}"
do
  cp "${ANDROID_ICON_PACK_LOCATION}/${resolution}/ic_launcher.png" "${ANDROID_ICON_PACK_DESTINATION}/${resolution}/ic_launcher.png"
  cp "${ANDROID_ICON_PACK_LOCATION}/${resolution}/ic_launcher_round.png" "${ANDROID_ICON_PACK_DESTINATION}/${resolution}/ic_launcher_round.png"
done

print_divider
# Copy iOS icons
echo "Copying iOS icons"
echo "Using icons at $IOS_ICON_PACK_LOCATION"

cp -a $IOS_ICON_PACK_LOCATION $IOS_ICON_PACK_DESTINATION

print_footer
