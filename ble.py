from time import sleep
import pygatt
import pandas as pd

class BLE():
    def __init__(self, address):
        
        # Bluetooth UUIDs
        self.RX_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"
        self.TX_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"



        # ESP32 Mac address
        self.DEVICE_ADDRESS = address

        # Create bluetooth adapter object
        self.adapter = pygatt.GATTToolBackend()

        # Initialize device object
        self.device = None
        self.connected = False
        
        # Dataframe where sensor data is recorded in
        self.df = pd.DataFrame(columns=['time','vl','vr','hl','hr'])
        self.data_cols = ['vl','vr','hl','hr']
        self.data = []
        self.filename = ''
    

    # Callback function that will be called whenever new data is received
    def handle_data(self, handle, value):
        message = value.decode("utf-8").split(",")
        self.data.append(message)
        #print(f"Incoming value: {self.data}")
        #self.df.loc[len(self.df)] = self.data

    # Establish connection to ESP32
    def connect(self):
        try:
            self.adapter.start()
            self.device = self.adapter.connect(self.DEVICE_ADDRESS)
            #self.device.subscribe(self.RX_UUID, callback=self.handle_data)
            characteristic = self.device.char_read(self.RX_UUID)

            # Read the value of the characteristic
            value = characteristic.read()
            print(f"Reading: {value}")

            print("Subscribed to RX_UUID")
            self.connected = True

        except Exception as e:
            print(e)
            self.connected = False

        finally:
            return self.connected

    # Start recording
    def start_record(self, recTime, filename):
    
        self.filename = filename
        
        try:
            self.device.char_write(self.TX_UUID, bytearray(str(recTime),'utf-8'))
            self.device.char_write(self.TX_UUID, bytearray("on",'utf-8'))
            
            
        except Exception as e:
            print("No device connected")
            print(e)

    # Stop recording
    def stop_record(self):
            
        try:
            self.device.char_write(self.TX_UUID, bytearray("off",'utf-8'))
            print(f"Dataframe: {self.df}")

        except Exception as e:
            print(e)





