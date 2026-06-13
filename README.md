<div align="center">
  
# 🐾 AgyPet (Antigravity Desktop Pet)

**A dynamic, cross-platform desktop companion & AI hardware bridge.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OS Support](https://img.shields.io/badge/OS-Windows%20%7C%20macOS-lightgrey.svg)]()

[English](#english) | [简体中文](#简体中文)

</div>

---

## 📖 Introduction / 项目简介

**AgyPet** is not just another desktop pet. It is a powerful, cross-platform bridge designed to visually and physically manifest the state of your AI Agents (like the Antigravity IDE). 

**AgyPet** 不仅仅是一个桌面宠物。它是一个强大的跨平台桥梁，旨在将您的 AI Agent（例如 Antigravity IDE）的运行状态，通过屏幕视觉和物理硬件实时具象化。

Whenever your AI is "Thinking", "Waiting for Approval", or encountering an "Error", AgyPet reflects this instantly through:
当您的 AI 处于“思考中”、“等待审批”或“报错”时，AgyPet 会通过以下两种方式瞬间做出反应：
1. **Desktop UI**: A sleek, transparent, frameless widget with fluid GIF animations and sound effects. (桌面悬浮窗动画与语音)
2. **Hardware IoT**: Real-time transmission of state codes via Bluetooth Low Energy (BLE) or Serial Port to external microcontrollers (e.g., ESP32) to trigger physical LEDs, servos, or buzzers. (通过蓝牙/串口驱动外部物理硬件硬件)

---

## 🖼️ Showcase / 视听效果预览

### Voice Profiles (多套专属 AI 语音包)
AgyPet features multiple built-in voice personalities (Master, Papa, Boss, Brother, Baby). Listen to some samples from the **"Master (主人)"** profile:
- 🟢 [Idle (空闲待机)](assets/sounds/zhuren/idle.mp3)
- 🔵 [Thinking (思考中)](assets/sounds/zhuren/thinking.mp3)
- 🟠 [Waiting (等待审批)](assets/sounds/zhuren/waiting.mp3)
- 🔴 [Error (执行报错)](assets/sounds/zhuren/error.mp3)

### Desktop Pet UI States (桌面悬浮窗状态)
<p align="center">
  <img src="docs/screenshots/agy-pet-idle.png" width="200" />
  <img src="docs/screenshots/agy-pet-thinking.png" width="200" />
  <img src="docs/screenshots/agy-pet-waiting.png" width="200" />
  <img src="docs/screenshots/agy-pet-error.png" width="200" />
</p>

### Live Core Animations (核心动态引擎素材)
<p align="center">
  <img src="assets/gifs/idle.gif" width="150" />
  <img src="assets/gifs/thinking.gif" width="150" />
  <img src="assets/gifs/waiting.gif" width="150" />
  <img src="assets/gifs/error.gif" width="150" />
</p>

### Task Completion Fireworks (任务完成满屏烟花特效)
<p align="center">
  <img src="docs/screenshots/apt-pet-fireworks-ui.png" width="800" />
</p>

---

## ✨ Core Features / 核心特性

- 🖥️ **Cross-Platform System Tray**: Perfectly supports Windows and macOS. Utilizes a true multi-processing architecture to bypass macOS main-thread UI restrictions. (真正的多进程系统托盘驻留，完美绕过 Mac 崩溃限制)
- 🛜 **Hardware Connectivity**: Built-in support for BLE (Bluetooth Low Energy) MAC/Name scanning and legacy USB Serial (SPP). (内置蓝牙扫描重连与传统串口支持)
- 🎨 **Modern Aesthetics**: Frameless capsule design, Catppuccin color palette, and dynamic GIF engines running on a transparent canvas. (无边框胶囊 UI 与自研透明 GIF 引擎)
- 🎆 **Task Completion Fireworks**: Procedurally generated, click-through, transparent fireworks overlay whenever the AI successfully completes a task. (算法生成的鼠标穿透全屏烟花特效，任务完成瞬间引爆满满成就感)
- ⚙️ **Hot-Swappable Configuration**: Change target Bluetooth devices, serial ports, or Agent log directories on the fly via the built-in GUI without restarting. (图形化热插拔配置)
- 🌐 **HTTP Webhook Integration**: Instantly sends POST requests with state data to any configured URL when the AI state changes. (支持实时向配置的 URL 触发 HTTP POST 状态变更回调)
- 🗣️ **Multiple Voice Profiles**: Built-in support for switching between different AI voice personalities (Papa, Master, Boss, Brother, Honey) to customize your companion's addressing style. (多套配音方案切换，随心选择您的专属 AI 称呼)
- 🪶 **Headless Mode**: Includes a `main.py` CLI script to run the state-bridge daemon silently on headless servers. (支持无 UI 静默后台运行)

---

## 🚀 Quick Start / 快速开始

### 1. Installation / 安装环境
Make sure you have Python 3.10+ installed.

```bash
# Clone the repository (克隆代码库)
git clone https://github.com/YourUsername/agy-pet.git
cd agy-pet

# Create and activate virtual environment (创建虚拟环境)
python -m venv venv
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies (安装依赖)
pip install -r requirements.txt
```

### 2. Running / 运行项目
You can run the full Desktop Widget mode (运行带 UI 的完整桌面模式):
```bash
pythonw src/app.py
```
Or run the headless CLI mode for server environments (或者运行纯命令行模式):
```bash
python src/main.py --mode ble --ble-name AgyPet
```

## 🔌 Hardware Integration Guide / 硬件接入指南

AgyPet sends a 1-byte state code (`0x01` to `0x04`) to your microcontroller. 
AgyPet 会发送 1字节 的十六进制状态码给单片机：
* `0x01` = IDLE (空闲)
* `0x02` = THINKING (思考中)
* `0x03` = WAITING_CONFIRM (等待人工审批)
* `0x04` = ERROR (执行报错)

### 1. Serial Port (USB) Example / 串口接入示例
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
      // IDLE: Turn off LED
      digitalWrite(LED_BUILTIN, LOW);
    } else if (state == 0x02) {
      // THINKING: Blink fast
      digitalWrite(LED_BUILTIN, HIGH);
      delay(100);
      digitalWrite(LED_BUILTIN, LOW);
    } else if (state == 0x03) {
      // WAITING: Solid ON
      digitalWrite(LED_BUILTIN, HIGH);
    }
  }
}
```

### 2. Bluetooth LE (BLE) Example / 蓝牙低功耗接入示例
For ESP32, using the highly optimized `h2zero/NimBLE-Arduino` library (Crucial for bypassing Windows WinRT GATT discovery bugs).
对于 ESP32，强烈推荐使用 `NimBLE-Arduino` 库（解决 Windows WinRT 底层由于安全策略导致的 GATT 服务 Unreachable 报错）。

```cpp
#include <NimBLEDevice.h>
#include <Adafruit_NeoPixel.h>

// ⚠️ Must match the UUIDs in AgyPet config
#define SERVICE_UUID        "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define CHARACTERISTIC_UUID "beb5483e-36e1-4688-b7f5-ea07361b26a8"

class MyCallbacks: public NimBLECharacteristicCallbacks {
    void onWrite(NimBLECharacteristic *pCharacteristic) {
      std::string value = pCharacteristic->getValue();
      if (value.length() > 0) {
        uint8_t state = (uint8_t)value[0]; 
        if (state == 0x00) return; // Ignore keep-alive pings
        
        Serial.printf("Received State: 0x%02X\n", state);
        // Add your hardware control logic here (0x01: IDLE, 0x02: THINKING, etc.)
      }
    }
};

void setup() {
  Serial.begin(115200);

  // Enable Security so Windows WinRT can pair with it securely
  NimBLEDevice::setSecurityAuth(true, true, true);
  NimBLEDevice::setSecurityIOCap(BLE_HS_IO_NO_INPUT_OUTPUT);
  NimBLEDevice::setSecurityInitKey(BLE_SM_PAIR_KEY_DIST_ENC | BLE_SM_PAIR_KEY_DIST_ID);

  NimBLEDevice::init("AgyPet-Link"); // Device Name
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
  pAdvertising->setAppearance(0x03C0); // ⚠️ CRITICAL: Gamepad appearance forces Windows UI to show it
  pAdvertising->setScanResponse(true);
  NimBLEDevice::startAdvertising();
  Serial.println("BLE Ready. Waiting for AgyPet to connect...");
}

void loop() {
  delay(2000);
}
```

> **⚠️ Windows Pairing Requirement (Windows 蓝牙必读)**: 
> Because of Windows security policies, you **MUST** manually pair the device in `Windows Settings -> Bluetooth & devices` before AgyPet can connect. The device will appear with a 🎮 Gamepad icon. (由于 Windows 安全策略，您**必须**先在 Windows 系统设置中手动点击配对该设备（带游戏手柄图标），然后桌面宠物才能成功连接，否则会一直报错 Unreachable)。

### 3. Troubleshooting Connection Issues / 连接排错指南
If AgyPet fails to connect to your BLE or Serial hardware, you can easily view detailed diagnostic logs:
如果 AgyPet 无法连接到您的蓝牙或串口硬件，您可以查看底层连接日志：
1. **Right-click** on the AgyPet desktop widget. (右键点击桌面宠物)
2. Select **`📂 Open Hardware Log`**. (选择打开硬件日志)
3. A text file (`agypet_hardware.log`) will open showing timestamped records of every scan attempt, connection timeout, and data transmission. (此时会打开日志文件，包含所有的蓝牙扫描、串口握手、以及发包记录)

---

## 🧪 Local Mock Testing / 本地虚拟测试指南

If you don't have physical ESP32 or Arduino hardware on hand, you can fully test AgyPet's communication logic using local mock testing tools.
如果您手头没有 ESP32 或 Arduino 等物理硬件，可以通过以下本地虚拟测试方案，完美测试 AgyPet 的硬件联动逻辑：

### 1. HTTP Webhook Testing (Easiest / 最省事)
Run the built-in webhook listener. It will open a floating window that changes colors like a physical LED based on AgyPet's state.
运行内置的 Webhook 测试脚本，它会弹出一个悬浮窗，像真实的物理 LED 灯一样随 AgyPet 的状态实时变色。
```bash
python mock_webhook_hardware.py
```
*Configure AgyPet Settings > Webhook URL to: `http://127.0.0.1:8888`*

### 2. Bluetooth LE (BLE) Testing (Using Phone / 手机模拟)
Due to strict OS limitations on Windows acting as a BLE Server, the best way to simulate BLE hardware is using your smartphone.
由于 Windows 系统的底层驱动限制，测试蓝牙硬件模拟的最佳方式是使用您的智能手机：
1. Download **nRF Connect for Mobile** (iOS/Android).
2. Go to the **Advertiser** (Server) tab.
3. Create a new configuration with Device Name: `AgyPet`.
4. Add Service UUID: `4fafc201-1fb5-459e-8fcc-c5c9c331914b`.
5. Add Characteristic UUID: `beb5483e-36e1-4688-b7f5-ea07361b26a8` and check the `WRITE` property.
6. **⚠️ CRITICAL**: You MUST check the **`Connectable`** option in the Advertising Configuration. If left unchecked, Windows will silently fail to connect with a "Device Not Found" error. (必须在广播配置中勾选 `Connectable` 可连接选项，否则 Windows 会由于底层驱动限制直接拒绝连接)
7. Start advertising, then scan and connect via AgyPet Desktop settings.

### 3. Serial Port Testing (Requires Driver / 需装驱动)
To test serial communication locally, you must install a virtual COM port driver (like `com0com`) to pair two ports (e.g., COM3 and COM4).
测试真实串口协议，必须在电脑上安装虚拟串口驱动（如免费的 `com0com`），创建互相连通的虚拟 COM3 和 COM4。
```bash
python mock_serial_hardware.py
```
*Configure AgyPet to connect to `COM3`, and the test script will automatically listen and receive data on `COM4`.*

---

## 📦 Building / 编译打包

### ☁️ Automated Cloud Build (Recommended)
This project is equipped with **GitHub Actions**. You don't need a Mac or a Linux machine to compile cross-platform versions!
1. Go to the **Actions** tab on your GitHub repository.
2. Select **Cross-Platform Release** and click **Run workflow**.
3. In 2 minutes, GitHub will automatically compile and provide download links for `.exe` (Windows), `.dmg` (macOS), and Linux executable binaries!

### Windows (.exe) Local Build
Run the automated build script. The compiled executable will appear in `dist/`.
```cmd
.\build.bat
```

### macOS (.app & .dmg) Local Build
*Note: You must run this on a Mac.*
```bash
bash build_mac.sh
```

---

## 🏗️ Architecture / 工程目录

```text
agy-pet/
├── assets/             # Audio (.mp3) and Animation (.gif) resources
├── src/                # Core Application Source Code
│   ├── app.py          # Desktop GUI Entry Point
│   ├── main.py         # Headless CLI Entry Point
│   ├── desktop_pet_ui.py
│   ├── pet_sender.py   # Serial/BLE communication bridge
│   ├── state_parser.py # Log watcher for AI state changes
│   ├── tray_icon.py    # Multi-processed system tray
│   └── config_manager.py
├── tools/              # Utility scripts
├── build.bat           # Windows PyInstaller build script
├── build_mac.sh        # macOS PyInstaller build script
└── requirements.txt    
```

---

## 🤝 Contributing / 参与贡献
As an open-source project, we welcome all PRs, issues, and feature requests!
作为开源项目，我们极度欢迎任何形式的代码贡献、Issue 和新想法！

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License / 开源协议
Distributed under the MIT License. See `LICENSE` for more information.
