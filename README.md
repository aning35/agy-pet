<div align="center">
  
# 🐾 AgyPet (Antigravity Desktop Pet)

<img src="docs/logo.png" width="150" style="border-radius: 25px" />

**A dynamic, cross-platform desktop companion & AI hardware bridge.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OS Support](https://img.shields.io/badge/OS-Windows%20%7C%20macOS-lightgrey.svg)]()

[English](README.md) | [简体中文](README_zh.md)

</div>

---

## 📖 Introduction

**AgyPet** is not just another desktop pet. It is a powerful, cross-platform bridge designed to visually and physically manifest the state of your AI Agents (like the Antigravity IDE). 

Whenever your AI is "Thinking", "Waiting for Approval", or encountering an "Error", AgyPet reflects this instantly through:
1. **Desktop UI**: A sleek, transparent, frameless widget with fluid GIF animations and sound effects.
2. **Hardware IoT**: Real-time transmission of state codes via Bluetooth Low Energy (BLE) or Serial Port to external microcontrollers (e.g., ESP32) to trigger physical LEDs, servos, or buzzers.

---

## 🖼️ Showcase

### Voice Profiles
AgyPet features multiple built-in voice personalities (Master, Papa, Boss, Brother, Baby). Listen to some samples from the **"Master"** profile:
- 🟢 [Idle](assets/sounds/zhuren/idle.mp3)
- 🔵 [Thinking](assets/sounds/zhuren/thinking.mp3)
- 🟠 [Waiting](assets/sounds/zhuren/waiting.mp3)
- 🔴 [Error](assets/sounds/zhuren/error.mp3)

### Desktop Pet UI States
<p align="center">
  <img src="docs/screenshots/agy-pet-idle.png" width="200" />
  <img src="docs/screenshots/agy-pet-thinking.png" width="200" />
  <img src="docs/screenshots/agy-pet-waiting.png" width="200" />
  <img src="docs/screenshots/agy-pet-error.png" width="200" />
</p>

### Live Core Animations
<p align="center">
  <img src="assets/gifs/idle.gif" width="150" />
  <img src="assets/gifs/thinking.gif" width="150" />
  <img src="assets/gifs/waiting.gif" width="150" />
  <img src="assets/gifs/error.gif" width="150" />
</p>

### Task Completion Fireworks
<p align="center">
  <img src="docs/screenshots/apt-pet-fireworks-ui.png" width="800" />
</p>

---

## ✨ Core Features

- 🖥️ **Cross-Platform System Tray**: Perfectly supports Windows and macOS. Utilizes a true multi-processing architecture to bypass macOS main-thread UI restrictions.
- 🎆 **Smart Context Menu & System Tray**: Right-click the pet to trigger actions (like "Fireworks"), or use the system tray/menu bar icon to toggle visibility, manage settings, and securely run in the background.
- 🛜 **Hardware Connectivity**: Built-in support for BLE (Bluetooth Low Energy) MAC/Name scanning and legacy USB Serial (SPP).
- 🎨 **Modern Aesthetics**: Frameless capsule design, Catppuccin color palette, and dynamic GIF engines running on a transparent canvas.
- ⚙️ **Hot-Swappable Configuration**: Change target Bluetooth devices, serial ports, or Agent log directories on the fly via the built-in GUI without restarting.
- 🌐 **HTTP Webhook Integration**: Instantly sends POST requests with state data to any configured URL when the AI state changes.
- 🗣️ **Multiple Voice Profiles**: Built-in support for switching between different AI voice personalities (Papa, Master, Boss, Brother, Honey) to customize your companion's addressing style.
- 🪶 **Headless Mode**: Includes a `main.py` CLI script to run the state-bridge daemon silently on headless servers.

---

## 🚀 Quick Start

### 1. Installation
Make sure you have Python 3.10+ installed.

```bash
# Clone the repository
git clone https://github.com/aning35/agy-pet.git
cd agy-pet

# Create and activate virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Running
You can run the full Desktop Widget mode:
```bash
pythonw src/app.py
```
Or run the headless CLI mode for server environments:
```bash
python src/main.py --mode ble --ble-name AgyPet
```

## 🔌 Hardware Integration Guide

AgyPet sends a 1-byte state code (`0x01` to `0x04`) to your microcontroller:
* `0x01` = IDLE
* `0x02` = THINKING
* `0x03` = WAITING_CONFIRM
* `0x04` = ERROR

### 1. Serial Port (USB) Example
For Arduino Nano, ESP32, or any board with USB Serial.
```cpp
void setup() {
  Serial.begin(115200);
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  if (Serial.available() > 0) {
    int state = Serial.read();
    
    if (state == 0x01) {
      digitalWrite(LED_BUILTIN, LOW);
    } else if (state == 0x02) {
      digitalWrite(LED_BUILTIN, HIGH);
      delay(100);
      digitalWrite(LED_BUILTIN, LOW);
    } else if (state == 0x03) {
      digitalWrite(LED_BUILTIN, HIGH);
    }
  }
}
```

### 2. Bluetooth LE (BLE) Example
For ESP32, using the highly optimized `h2zero/NimBLE-Arduino` library (Crucial for bypassing Windows WinRT GATT discovery bugs).

```cpp
#include <NimBLEDevice.h>

#define SERVICE_UUID        "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define CHARACTERISTIC_UUID "beb5483e-36e1-4688-b7f5-ea07361b26a8"

class MyCallbacks: public NimBLECharacteristicCallbacks {
    void onWrite(NimBLECharacteristic *pCharacteristic) {
      std::string value = pCharacteristic->getValue();
      if (value.length() > 0) {
        uint8_t state = (uint8_t)value[0]; 
        if (state == 0x00) return; // Ignore keep-alive pings
        
        Serial.printf("Received State: 0x%02X\n", state);
      }
    }
};

void setup() {
  Serial.begin(115200);

  NimBLEDevice::setSecurityAuth(true, true, true);
  NimBLEDevice::setSecurityIOCap(BLE_HS_IO_NO_INPUT_OUTPUT);
  NimBLEDevice::setSecurityInitKey(BLE_SM_PAIR_KEY_DIST_ENC | BLE_SM_PAIR_KEY_DIST_ID);

  NimBLEDevice::init("AgyPet"); // Device Name
  NimBLEServer *pServer = NimBLEDevice::createServer();
  NimBLEService *pService = pServer->createService(SERVICE_UUID);
  
  NimBLECharacteristic *pCharacteristic = pService->createCharacteristic(
                                         CHARACTERISTIC_UUID,
                                         NIMBLE_PROPERTY::READ | NIMBLE_PROPERTY::WRITE | NIMBLE_PROPERTY::WRITE_NR
                                       );
  uint8_t initialState = 0x01;
  pCharacteristic->setValue(&initialState, 1);
  pCharacteristic->setCallbacks(new MyCallbacks());
  pService->start();
  
  NimBLEAdvertising *pAdvertising = NimBLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->setAppearance(0x03C0); // ⚠️ CRITICAL: Gamepad appearance
  pAdvertising->setScanResponse(true);
  NimBLEDevice::startAdvertising();
}

void loop() { delay(2000); }
```

> **⚠️ Windows Pairing Requirement**: 
> Because of Windows security policies, you **MUST** manually pair the device in `Windows Settings -> Bluetooth & devices` before AgyPet can connect. The device will appear with a 🎮 Gamepad icon.

### 3. Troubleshooting Connection Issues
If AgyPet fails to connect to your hardware:
1. **Right-click** on the AgyPet desktop widget.
2. Select **`📂 Open Hardware Log`**.
3. A text file (`agypet_hardware.log`) will open showing timestamped records of every scan attempt and data transmission.

---

## 🧪 Local Mock Testing

If you don't have physical hardware, you can test the communication logic locally.

### 1. HTTP Webhook Testing (Easiest)
Run the built-in webhook listener:
```bash
python tests/mock_webhook_hardware.py
```
*Configure AgyPet Settings > Webhook URL to: `http://127.0.0.1:8888`*

### 2. Serial Port Testing
Test serial communication locally using a virtual COM port driver (like `com0com`) to pair two ports (e.g., COM3 and COM4).
```bash
python tests/mock_serial_hardware.py
```
*Configure AgyPet to connect to `COM3`, and the test script will automatically listen on `COM4`.*

---

## 📦 Building

### ☁️ Automated Cloud Build (Recommended)
This project is equipped with **GitHub Actions**. You don't need a Mac or a Linux machine to compile cross-platform versions!
1. Go to the **Actions** tab on your GitHub repository.
2. Select **Cross-Platform Release** and click **Run workflow**.
3. In 2 minutes, GitHub will automatically compile `.exe` (Windows) and `.dmg` (macOS) binaries!

### Windows (.exe) Local Build
```cmd
.\build.bat
```

### macOS (.app & .dmg) Local Build
First, run the script to build the basic `.app` bundle:
```bash
bash build_mac.sh
```
To further package it into a styled `.dmg` installer image with background and icon layout, install and use `dmgbuild`:
```bash
pip install dmgbuild
dmgbuild -s settings.py 'AgyPet' AgyPet.dmg
```

---

## 🤝 Contributing
As an open-source project, we welcome all PRs, issues, and feature requests!

## 📄 License
Distributed under the MIT License. See `LICENSE` for more information.
