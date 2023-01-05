from bleak import BleakClient
import pandas as pd
import numpy as np
import datetime
import time
import asyncio
import os

mac = ("24:0A:C4:62:52:FE") #dev nxn

connected = False
RX_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"
TX_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"


class bt_daq():
    def __init__(self, mac):
        self.mac = mac
        self.RX_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"
        self.TX_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
        self.recording = []
        self.txOn = bytearray("on",'utf-8')
        self.txOff = bytearray("off",'utf-8')
        self.rec = np.zeros([1,5])
        self.dataframe = pd.DataFrame(self.rec, columns=['time', 'vl', 'vr', 'hl', 'hr'])
        self.client = BleakClient(mac, timeout=10)
        
    def callback(self, sender: int, data: bytearray):
        # Decode data from bytearrays to strings and split them at the "," delimiter
        self.rec = data.decode("utf-8").split(",")
        print(self.rec)
        # Convert every element of the row into an integer
        for idx, element in enumerate(self.rec):
            self.rec[idx] = int(element)

        # Add that array as a row to the dataframe
        self.dataframe.loc[len(self.dataframe)] = self.rec
    
    async def connect(self):
        await self.client.connect()
        if self.client.is_connected:
            return True
        else:
            return False

    async def send_start_command(self):
        await self.client.start_notify(self.RX_UUID, self.callback)
        await self.client.write_gatt_char(self.TX_UUID, self.txOn)
        return True

    async def send_stop_command(self):
        await self.client.write_gatt_char(self.TX_UUID, self.txOff)
        return True

    async def get_data(self, duration):
        try:
            async with BleakClient(self.mac) as client:
                    
                if client.is_connected:
                        await client.start_notify(self.RX_UUID, self.callback)
                    
                        await client.write_gatt_char(self.TX_UUID, bytearray(str(duration),'utf-8'))
                        await client.write_gatt_char(self.TX_UUID, self.txOn)
                        time.sleep(duration)
                        await client.write_gatt_char(self.TX_UUID, self.txOff)
                        success = True

                else:
                    print(f'BT Device with MAC {self.mac} not found')

        except Exception as e:
            print(e)
            success = False
        finally:      
            print("Exiting")
            return success
        
    def export_data(self):
        print("Exporting CSV")
        self.dataframe.to_csv(path_or_buf=f"./data_export/data_{datetime.datetime.now().isoformat()}.csv", sep=',', index_label="Index", na_rep='NaN')


async def main():
            success = await ESP32_1.get_data(2)
            if success:
                ESP32_1.export_data()

            else:
                print("not successful")
    
connected = False
ESP32_1 = bt_daq(mac)
asyncio.run(main())