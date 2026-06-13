# AgyPet ESP32-S3 Hardware Example

This directory contains an Arduino C++ sketch (`ESP32S3_AgyPet.ino`) that allows your ESP32-S3 to act as an external hardware peripheral for the AgyPet desktop application.

## Features
- **Dual Mode Connectivity:** Works with AgyPet over both **Bluetooth LE (BLE)** and **Serial (USB)**.
- **Visual Status Indicator:** Uses an onboard WS2812 (NeoPixel) RGB LED to display AgyPet's current state.

## LED State Colors
| State Code | Meaning            | LED Color   |
|------------|--------------------|-------------|
| 0x01       | IDLE               | Green       |
| 0x02       | THINKING           | Blue        |
| 0x03       | WAITING_CONFIRM    | Orange      |
| 0x04       | ERROR              | Red         |

## Requirements & Setup
1. **Arduino IDE:** Install the Arduino IDE and the **ESP32** board support package.
2. **Library:** Install the `Adafruit NeoPixel` library via the Arduino Library Manager.
3. **Board Selection:** Select your specific ESP32-S3 board (e.g., "ESP32S3 Dev Module").
4. **Pin Configuration:** 
   The sketch assumes your board's WS2812 LED is connected to **GPIO 48**, which is standard for many ESP32-S3 development boards. If your board uses a different pin (e.g., GPIO 8, GPIO 38), simply change the `LED_PIN` macro at the top of the `.ino` file.

## How to Use
1. Flash the code to your ESP32-S3.
2. Open the AgyPet desktop application.
3. Go to **Settings** and select your desired connection mode:
   - **Bluetooth LE:** Make sure your PC's Bluetooth is on. AgyPet will automatically scan for and connect to `AgyPet-ESP32S3`.
   - **Serial Port:** Select the correct COM port and leave the Baud Rate at `115200`.
4. As AgyPet changes state (e.g., when thinking or waiting for confirmation), the LED on your ESP32-S3 will change colors accordingly!
