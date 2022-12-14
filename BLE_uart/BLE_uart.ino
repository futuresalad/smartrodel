
/*
    Video: https://www.youtube.com/watch?v=oCMOYS71NIU
    Based on Neil Kolban example for IDF: https://github.com/nkolban/esp32-snippets/blob/master/cpp_utils/tests/BLE%20Tests/SampleNotify.cpp
    Ported to Arduino ESP32 by Evandro Copercini

   Create a BLE server that, once we receive a connection, will send periodic notifications.
   The service advertises itself as: 6E400001-B5A3-F393-E0A9-E50E24DCCA9E
   Has a characteristic of: 6E400002-B5A3-F393-E0A9-E50E24DCCA9E - used for receiving data with "WRITE" 
   Has a characteristic of: 6E400003-B5A3-F393-E0A9-E50E24DCCA9E - used to send data with  "NOTIFY"

   The design of creating the BLE server is:
   1. Create a BLE Server
   2. Create a BLE Service
   3. Create a BLE Characteristic on the Service
   4. Create a BLE Descriptor on the characteristic
   5. Start the service.
   6. Start advertising.

   In this example rxValue is the data received (only accessible inside that function).
   And txValue is the data to be sent, in this example just a byte incremented every second. 
*/
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

int PinVL = 27;
int PinVR = 14;
int PinHL = 12;
int PinHR = 13;

// Bluetooth config 
BLEServer *pServer = NULL;
BLECharacteristic * pTxCharacteristic;
BLECharacteristic * pTxCharacteristic_time;
bool deviceConnected = false;
bool oldDeviceConnected = false;

int sensorPins[4] = {27, 14, 12, 13};
int txValue[4] = {0, 0, 0, 0};

unsigned long lastTime = 0;
unsigned long timerDelay = 10; //100Hz sample rate
//unsigned long timerDelay = (1000/60); //60Hz sample rate

bool send_data = false;

// See the following for generating UUIDs:
// https://www.uuidgenerator.net/

#define SERVICE_UUID           "6E400001-B5A3-F393-E0A9-E50E24DCCA9E" // UART service UUID
#define CHARACTERISTIC_UUID_RX "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
#define CHARACTERISTIC_UUID_TX "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

class MyServerCallbacks: public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) {
      deviceConnected = true;
    };

    void onDisconnect(BLEServer* pServer) {
      deviceConnected = false;
    }
};

class MyCallbacks: public BLECharacteristicCallbacks {
    void onWrite(BLECharacteristic *pCharacteristic) {
      std::string rxValue = pCharacteristic->getValue();

      if (rxValue.length() > 0) {
        Serial.println("*********");
        Serial.print("Received Value: ");
        
        for (int i = 0; i < rxValue.length(); i++)
          Serial.print(rxValue[i]);

        Serial.println();
        Serial.println("*********");

       if (rxValue == "on") {
        Serial.println("Send data");
        send_data = true;
        
       }
       else if (rxValue == "off") {
        Serial.println("Stop data");
        send_data = false;
       }

   }
  }
};

void setup() {
  Serial.begin(115200);

  // Create the BLE Device
  BLEDevice::init("SmartRodelServer");

  // Create the BLE Server
  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());

  // Create the BLE Service
  BLEService *pService = pServer->createService(SERVICE_UUID);

  // Create a BLE Characteristic
  pTxCharacteristic = pService->createCharacteristic(
										CHARACTERISTIC_UUID_TX,
										BLECharacteristic::PROPERTY_NOTIFY
									);

                  
  pTxCharacteristic->addDescriptor(new BLE2902());

  BLECharacteristic * pRxCharacteristic = pService->createCharacteristic(
											 CHARACTERISTIC_UUID_RX,
											BLECharacteristic::PROPERTY_WRITE
										);


  pRxCharacteristic->setCallbacks(new MyCallbacks());

  // Start the service
  pService->start();

  // Start advertising
  pServer->getAdvertising()->start();
  Serial.println("Waiting a client connection to notify...");
}

void loop() {


      if (deviceConnected) {

        //Serial.println("Awaiting commands..");

      if  (send_data) {
          //Serial.println("Sending data");
          }
          char buffer[100];
          int start = millis();
          int now = 0;
          int last_meas = 0;
          

          while (send_data) {
            
                now = millis() - start;
                
                if ((now - last_meas) >= timerDelay) {
                   
                    last_meas = now;
                   
                   for (int i = 0; i < 4; i++){ 
                        txValue[i] = analogRead(sensorPins[i]);
                   }
                   
                sprintf(buffer, "%u,%u,%u,%u,%u ", now, txValue[0], txValue[1], txValue[2], txValue[3]);
                pTxCharacteristic->setValue(buffer);
                pTxCharacteristic->notify();
                
                //delay(10);
                }

         }        
         //Serial.println("Stopped data");
	    } 

    // disconnecting
    if (!deviceConnected && oldDeviceConnected) {
        send_data = false;
        delay(500); // give the bluetooth stack the chance to get things ready
        pServer->startAdvertising(); // restart advertising
        Serial.println("Disconnected, start advertising");
        oldDeviceConnected = deviceConnected;
    }
    // connecting
    if (deviceConnected && !oldDeviceConnected) {
		// do stuff here on connecting
        Serial.println("Device connected");
        oldDeviceConnected = deviceConnected;    }
}
