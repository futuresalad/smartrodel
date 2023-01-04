#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

// Bluetooth service and characteristics UUID's
#define SERVICE_UUID           "6E400001-B5A3-F393-E0A9-E50E24DCCA9E" // UART service UUID
#define CHARACTERISTIC_UUID_RX "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
#define CHARACTERISTIC_UUID_TX "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

// Bluetooth server config 
BLEServer *pServer = NULL;
BLECharacteristic * pTxCharacteristic;
BLECharacteristic * pTxCharacteristic_time;

// Connection Status
bool deviceConnected = false;
bool oldDeviceConnected = false;

// Measurement config
int sensorPins[4] = {27, 14, 12, 13};

// Initializing array containing measurements
int txValue[4] = {0, 0, 0, 0};

// Initializing timestamp of last measurement
unsigned long lastTime = 0;

// "Sending data"-flag, if true, client is notified 
bool send_data = false;

// Sample rate: 50Hz
unsigned long sample_delay = 1000/50;
//unsigned long sample_delay = 1000;

// Initializing time variables
int start = 0;
int now = 0;
int last_meas = 0;

// Initializing TX buffer
char buffer[64];

// Callback functions to handle incoming packets
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
          Serial.print("Received data: ");
          
         for (int i = 0; i < rxValue.length(); i++) {
              Serial.print(rxValue[i]);
            }
         Serial.println();
            
         if (rxValue == "on") {
            Serial.println("Start sending");
            send_data = true;
            }
         
         else {
            Serial.println("Stop sending");
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

    if (deviceConnected && send_data) {
       now = millis();
       start = millis();

       while(deviceConnected && send_data){
        
           now = millis() - start;
           
           if ((now - last_meas) >= sample_delay) {
                 last_meas = now;
                 
                 for (int i = 0; i < 4; i++){ 
                      txValue[i] = analogRead(sensorPins[i]);
                 }
                 
                 sprintf(buffer, "%u,%u,%u,%u,%u", now, txValue[0], txValue[1], txValue[2], txValue[3]);
                 Serial.print("Sending data: ");
                 Serial.println(buffer);
                 pTxCharacteristic->setValue(buffer);
                 pTxCharacteristic->notify();
                
                 }
           }
    }


    // disconnecting
    if (!deviceConnected && oldDeviceConnected) {
  
        delay(500); // give the bluetooth stack the chance to get things ready
        pServer->startAdvertising(); // restart advertising
        Serial.println("Disconnected, start advertising");
        oldDeviceConnected = deviceConnected;
    }
    
    // connecting
    if (deviceConnected && !oldDeviceConnected) {
        // do stuff here on connecting
        Serial.println("Device connected");
        oldDeviceConnected = deviceConnected;
    }
}
