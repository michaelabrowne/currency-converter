#!/usr/bin/env bash
# Currency Converter — macOS installer
# Usage: curl -fsSL https://raw.githubusercontent.com/michaelabrowne/currency-converter/develop/install.sh | bash
set -euo pipefail

APP_NAME="Currency Converter"
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

echo "==> Mounting disk image..."
MOUNT_POINT=$(hdiutil attach "$DMG" -nobrowse -quiet | grep '/Volumes' | cut -f3-)

echo "==> Installing to $INSTALL_DIR..."
rm -rf "$INSTALL_DIR/$APP_NAME.app"
cp -R "$MOUNT_POINT/$APP_NAME.app" "$INSTALL_DIR/"

echo "==> Removing quarantine flag..."
xattr -cr "$INSTALL_DIR/$APP_NAME.app"

echo "==> Cleaning up..."
hdiutil detach "$MOUNT_POINT" -quiet
rm -rf "$TMP"

echo ""
echo "  Currency Converter installed successfully."
echo "  Launching..."
open "$INSTALL_DIR/$APP_NAME.app"
