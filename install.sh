#!/usr/bin/env bash
# Currency Converter — macOS installer
# Usage: curl -fsSL https://raw.githubusercontent.com/michaelabrowne/currency-converter/develop/install.sh | bash
set -euo pipefail

REPO="michaelabrowne/currency-converter"
INSTALL_DIR="/Applications"

echo "==> Fetching latest release..."
DOWNLOAD_URL=$(curl -fsL "https://api.github.com/repos/$REPO/releases/latest" \
  | grep '"browser_download_url"' \
  | grep 'macOS' \
  | cut -d'"' -f4)

if [[ -z "$DOWNLOAD_URL" ]]; then
  echo "Error: could not find a macOS release. Check https://github.com/$REPO/releases"
  exit 1
fi

echo "==> Downloading $(basename "$DOWNLOAD_URL")..."
TMP=$(mktemp -d)
DMG="$TMP/CurrencyConverter.dmg"
curl -L --progress-bar "$DOWNLOAD_URL" -o "$DMG"

# Detach any existing Currency Converter volumes to avoid macOS auto-numbering
while IFS= read -r vol; do
  hdiutil detach "$vol" -quiet 2>/dev/null || true
done < <(find /Volumes -maxdepth 1 -name "Currency Converter*" -type d 2>/dev/null)

echo "==> Mounting disk image..."
hdiutil attach "$DMG" -nobrowse > /dev/null 2>&1

# Find the mounted volume (handles auto-numbered names like "Currency Converter 2")
MOUNT_POINT=$(find /Volumes -maxdepth 1 -name "Currency Converter*" -type d 2>/dev/null | sort | tail -1)
if [[ -z "$MOUNT_POINT" ]]; then
  echo "Error: could not find the mounted DMG volume."
  exit 1
fi

# Find the .app bundle inside (handles any bundle name)
APP_BUNDLE=$(find "$MOUNT_POINT" -maxdepth 1 -name "*.app" -type d | head -1)
if [[ -z "$APP_BUNDLE" ]]; then
  echo "Error: no .app bundle found inside the DMG."
  hdiutil detach "$MOUNT_POINT" -quiet
  exit 1
fi

APP_NAME=$(basename "$APP_BUNDLE")
echo "==> Installing $APP_NAME to $INSTALL_DIR..."
rm -rf "$INSTALL_DIR/$APP_NAME"
cp -R "$APP_BUNDLE" "$INSTALL_DIR/"

echo "==> Removing quarantine flag..."
xattr -cr "$INSTALL_DIR/$APP_NAME"

echo "==> Cleaning up..."
hdiutil detach "$MOUNT_POINT" -quiet
rm -rf "$TMP"

echo ""
echo "  $APP_NAME installed successfully."
echo "  Launching..."
open "$INSTALL_DIR/$APP_NAME"
