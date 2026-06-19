#!/bin/bash
# ==========================================
# AgyPet macOS Build Script
# ==========================================
# Note: This script MUST be executed on a Mac.
# PyInstaller does not support cross-compiling
# macOS apps from Windows.
# ==========================================

echo "Building AgyPet for macOS..."

# 1. Check if virtual environment is active
if ! command -v pyinstaller &> /dev/null
then
    echo "PyInstaller could not be found. Please ensure you are in a virtual environment with 'pip install -r requirements.txt' executed."
    exit 1
fi

# 2. Build the macOS .app bundle
# Note: macOS uses a colon (:) instead of semicolon (;) for --add-data paths
pyinstaller --clean --noconfirm --windowed \
    --add-data "assets/sounds:assets/sounds" \
    --add-data "assets/gifs:assets/gifs" \
    --add-data "assets/tray_icon.png:assets" \
    --icon="assets/icon.icns" \
    --name AgyPet \
    src/app.py

echo "Configuring Info.plist for UI and Permissions..."
plutil -replace LSUIElement -bool true dist/AgyPet.app/Contents/Info.plist || plutil -insert LSUIElement -bool true dist/AgyPet.app/Contents/Info.plist
plutil -replace NSBluetoothAlwaysUsageDescription -string "AgyPet needs Bluetooth access to connect to your smart pet hardware." dist/AgyPet.app/Contents/Info.plist || plutil -insert NSBluetoothAlwaysUsageDescription -string "AgyPet needs Bluetooth access to connect to your smart pet hardware." dist/AgyPet.app/Contents/Info.plist
plutil -replace NSBluetoothPeripheralUsageDescription -string "AgyPet needs Bluetooth access to connect to your smart pet hardware." dist/AgyPet.app/Contents/Info.plist || plutil -insert NSBluetoothPeripheralUsageDescription -string "AgyPet needs Bluetooth access to connect to your smart pet hardware." dist/AgyPet.app/Contents/Info.plist

echo "Re-signing the application bundle..."
codesign --force --deep --sign - dist/AgyPet.app

echo ""
echo "=========================================="
echo "Build complete! The AgyPet.app bundle is located in the dist/ folder."
echo "=========================================="
echo ""
echo "[How to create a DMG file]"
echo "Method 1: Use the built-in Disk Utility to wrap the dist/ folder into an Image."
echo "Method 2: Install dmgbuild and run it:"
echo "          pip install dmgbuild"
echo "          dmgbuild -s settings.py 'AgyPet' AgyPet.dmg"
