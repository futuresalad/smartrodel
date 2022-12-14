from bleak import BleakClient
import pandas as pd
import numpy as np
import datetime
import time
import asyncio
import plotly_express as px
import streamlit as st
import os

mac = ("30:C6:F7:DD:C7:F6")
success = False
ANGLE_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"
TX_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
img_path ="./icon.png"
st.set_page_config(page_title="SmartRodel Dashboard", page_icon=":snowflake:")

class bt_daq():
    def __init__(self, mac):
        self.mac = mac
        self.ANGLE_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"
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
        await self.client.start_notify(self.ANGLE_UUID, self.callback)
        await self.client.write_gatt_char(self.TX_UUID, self.txOn)
        return True

    async def send_stop_command(self):
        await self.client.write_gatt_char(self.TX_UUID, self.txOff)
        return True

    async def get_data(self, duration):
        try:
            async with BleakClient(self.mac) as client:
                    
                if client.is_connected:
                        await client.start_notify(self.ANGLE_UUID, self.callback)
                        await client.write_gatt_char(self.TX_UUID, self.txOn)
                        time.sleep(duration)
                        await client.write_gatt_char(self.TX_UUID, self.txOff)
                        success = True
        except:
            print("Could not connect to ESP32")
            success = False
        finally:      
            print("Exiting")
            return success
        
    def export_data(self):
        print("Exporting CSV")
        self.dataframe.to_csv(path_or_buf=f"./data_export/data_{datetime.datetime.now().isoformat()}.csv", sep=',', index_label="Index", na_rep='NaN')


def del_files(consent):
    if consent:

        try:
            for (dirpath, dirnames, filenames) in os.walk("./data_export"):
                for file in filenames:
                    os.remove(f'./data_export/{file}')
        except:
            pass

        finally:
            st.text("Files deleted")


async def main():

    f = []
    for (dirpath, dirnames, filenames) in os.walk("./data_export"):
        f.extend(filenames)
    
    success = False
    consent = False
    files_exist = False
    dl_filename = ""
    col1, col2= st.columns([1,3])

    with col1:
        
        st.image(img_path)
        
        if st.button("🔴 Start recording"):
            success = False
            try:
                with st.spinner('Recording'):
                    success = await ESP32_1.get_data(slider)

            except: 
                st.error("Not able to connect")
                success = False

        if success:
            st.text("Data recorded")
            ESP32_1.export_data()

        try:
            with open(f"./data_export/{dl_filename}", "rb") as file:

                st.download_button(
                label="💾 Download CSV",
                data=file,
                disabled=files_exist,
                file_name=dl_filename
                )
        except:
            st.button("💾 Download CSV", disabled=True)


    with col2:

        st.title("SmartRodel Dashboard")

        slider = st.slider(label="Aufnahmedauer in Sekunden", min_value=0, max_value=120, value=10, label_visibility="visible")
        
        dl_filename = st.selectbox("Aufnahemen", f, index=0, on_change=None, disabled=False, label_visibility="hidden")

        consent = st.checkbox('Yes, i want to delete all recordings')

        if consent:
            st.text("⚠️ All records will be permanently removed")
            consent = st.button("Clear data")

            del_files(consent)



success = False
ESP32_1 = bt_daq("30:C6:F7:DD:C7:F6")
asyncio.run(main())

