#include <Arduino.h>
#include <NimBLEDevice.h>
#include <Adafruit_NeoPixel.h>
#include <esp_mac.h>

#define STATE_IDLE             0x01
#define STATE_THINKING         0x02
#define STATE_WAITING_CONFIRM  0x03
#define STATE_ERROR            0x04

#define LED_PIN 48 
#define NUMPIXELS 1

Adafruit_NeoPixel pixels(NUMPIXELS, LED_PIN, NEO_GRB + NEO_KHZ800);

#define SERVICE_UUID           "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define CHARACTERISTIC_UUID    "beb5483e-36e1-4688-b7f5-ea07361b26a8"

NimBLEServer* pServer = NULL;
NimBLECharacteristic* pCharacteristic = NULL;
bool deviceConnected = false;
uint8_t currentState = STATE_IDLE;

void setLEDColor(uint8_t state) {
  pixels.clear();
  switch (state) {
    case STATE_IDLE: pixels.setPixelColor(0, pixels.Color(0, 255, 0)); break;
    case STATE_THINKING: pixels.setPixelColor(0, pixels.Color(0, 0, 255)); break;
    case STATE_WAITING_CONFIRM: pixels.setPixelColor(0, pixels.Color(255, 165, 0)); break;
    case STATE_ERROR: pixels.setPixelColor(0, pixels.Color(255, 0, 0)); break;
    default: pixels.setPixelColor(0, pixels.Color(255, 255, 255)); break;
  }
  pixels.show();
  currentState = state;
}

class MyServerCallbacks: public NimBLEServerCallbacks {
    void onConnect(NimBLEServer* pServer) {
      deviceConnected = true;
      Serial.println("BLE Client Connected!");
    }
    void onDisconnect(NimBLEServer* pServer) {
      deviceConnected = false;
      Serial.println("BLE Client Disconnected! Restarting advertising...");
      NimBLEDevice::startAdvertising();
    }
};

class MyCallbacks: public NimBLECharacteristicCallbacks {
    void onWrite(NimBLECharacteristic *pCharacteristic) {
      std::string value = pCharacteristic->getValue();
      if (value.length() > 0) {
        uint8_t receivedState = (uint8_t)value[0];
        if (receivedState == 0x00) return; // Ignore keep-alive pings from desktop app
        Serial.print("Received BLE State: 0x");
        Serial.println(receivedState, HEX);
        setLEDColor(receivedState);
      }
    }
};

void setup() {
  Serial.begin(115200);
  pixels.begin();
  pixels.setBrightness(50);
  setLEDColor(STATE_IDLE);

  // Enable Security so Windows WinRT can pair with it securely
  NimBLEDevice::setSecurityAuth(true, true, true);
  NimBLEDevice::setSecurityIOCap(BLE_HS_IO_NO_INPUT_OUTPUT);
  NimBLEDevice::setSecurityInitKey(BLE_SM_PAIR_KEY_DIST_ENC | BLE_SM_PAIR_KEY_DIST_ID);

  NimBLEDevice::init("AgyPet-Link");
  pServer = NimBLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());
  
  NimBLEService *pService = pServer->createService(SERVICE_UUID);

  pCharacteristic = pService->createCharacteristic(
                      CHARACTERISTIC_UUID,
                      NIMBLE_PROPERTY::READ | NIMBLE_PROPERTY::WRITE | NIMBLE_PROPERTY::WRITE_NR
                    );
  pCharacteristic->setValue(&currentState, 1);
  pCharacteristic->setCallbacks(new MyCallbacks());

  pService->start();

  NimBLEAdvertising *pAdvertising = NimBLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->setAppearance(0x03C0); // Gamepad appearance forces Windows UI to show it
  pAdvertising->setScanResponse(true);
  NimBLEDevice::startAdvertising();
  
  Serial.println("AgyPet ESP32-S3 Hardware Ready.");
}

void loop() {
  if (Serial.available() > 0) {
    uint8_t incomingByte = Serial.read();
    Serial.print("Received Serial State: 0x");
    Serial.println(incomingByte, HEX);
    setLEDColor(incomingByte);
  }
  delay(10);
}
