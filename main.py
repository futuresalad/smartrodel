from bleak import BleakClient
import pandas as pd
import numpy as np
import datetime
import time
import asyncio
import streamlit as st
import os

#mac = ("30:C6:F7:DD:C7:F6") dev nxn
mac = ("24:0A:C4:62:52:FE")
connected = False
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


def refresh_files():
    f = []
    for (dirpath, dirnames, filenames) in os.walk("./data_export"):
        f.extend(filenames)
    
    return f

async def main():
    f = refresh_files()
    
    success = False
    consent = False
    sl_val = 20
    files_exist = False
    dl_filename = ""
    col1, col2= st.columns([1,3])


    with col2:

        st.title("SmartRodel Dashboard")

        sl_val = st.slider(label="Recording duration in seconds", min_value=0, max_value=120, value=sl_val, label_visibility="visible")
        
        dl_filename = st.selectbox("Aufnahemen", f, index=0, on_change=None, disabled=False, label_visibility="hidden")

        consent = st.checkbox('Yes, i want to delete all recordings')

        if consent:
            st.text("⚠️ All records will be permanently removed")
            consent = st.button("Clear data")

            del_files(consent)

    with col1:
        
        st.image(img_path)
        if connected:
            st.success("Device found")
        

        if st.button("🔴 Start recording"):
            success = False
            try:
                with st.spinner('Recording'):
                    success = await ESP32_1.get_data(sl_val)
                    st.text("Data recorded")

            except Exception as e: 
                print(e)
                st.error("Not able to connect")
                success = False

        if success:
            
            ESP32_1.export_data()
        
        if st.button("♻️ Refresh records"):
            f = refresh_files()


    try:

        chart_data = pd.read_csv(f'./data_export/{dl_filename}', usecols=['vl','vr','hl','hr'])
        st.line_chart(chart_data)

    except:
        st.info("No recording selected")



    with col1:
        try:
            
            with open(f"./data_export/{dl_filename}", "rb") as file:

                st.download_button(
                label="⬇️ Download CSV",
                data=file,
                disabled=files_exist,
                file_name=dl_filename
                )
        except:
            st.button("💾 Download CSV", disabled=True)


connected = False
ESP32_1 = bt_daq(mac)
asyncio.run(main())

