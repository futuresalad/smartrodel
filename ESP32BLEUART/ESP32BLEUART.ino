/*********
  Rui Santos
  Complete instructions at https://RandomNerdTutorials.com/esp32-ble-server-client/
  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files.
  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
*********/

#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <Wire.h>

//BLE server name
#define bleServerName "ESP32Rodel"

float angleFloat = 0;

// Timer variables
unsigned long lastTime = 0;
unsigned long timerDelay = 1/60;

bool deviceConnected = false;

// Initialize pServer
BLEServer *pServer = NULL;

// See the following for generating UUIDs:
// https://www.uuidgenerator.net/
#define SERVICE_UUID "91bad492-b950-4226-aa2b-4ede9fa42f59"

BLECharacteristic angleChraracteristic("cba1d466-344c-4be3-ab3f-189f80dd7518", BLECharacteristic::PROPERTY_NOTIFY);
BLEDescriptor angleDescriptor(BLEUUID((uint16_t)0x2902));

//Setup callbacks onConnect and onDisconnect
class MyServerCallbacks: public BLEServerCallbacks {
  void onConnect(BLEServer* pServer) {
    deviceConnected = true;
  };
  void onDisconnect(BLEServer* pServer) {
    deviceConnected = false;
  }
};


void setup() {
  // Start serial communication 
  Serial.begin(115200);

  // Create the BLE Device
  BLEDevice::init(bleServerName);

  // Create the BLE Server
  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());

  // Create the BLE Service
  BLEService *angleService = pServer->createService(SERVICE_UUID);

  // Create BLE Characteristics and Create a BLE Descriptor
  angleService->addCharacteristic(&angleChraracteristic);
  angleDescriptor.setValue("Kuvenwinkel in grad");
  angleChraracteristic.addDescriptor(&angleDescriptor);
  
  // Start the service
  angleService->start();
  
  // Start advertising
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pServer->getAdvertising()->start();
  Serial.println("Waiting a client connection to notify...");
}

void loop() {
  if (deviceConnected) {
    if ((millis() - lastTime) > timerDelay) {

      angleFloat++;
      static char angleStr[6];
      dtostrf(angleFloat, 6, 2, angleStr);
      angleChraracteristic.setValue(angleStr);
      angleChraracteristic.notify();
      Serial.print("Kuvenwinkel: ");
      Serial.print(angleStr);
      Serial.println("°");
      
      lastTime = millis();
      
      if (angleFloat > 100) {
        angleFloat = 0;
      }
      
    }
  }

 if (!deviceConnected) {
  delay(500);
  Serial.println("start advertising");
  pServer->startAdvertising();
  
 }
}
