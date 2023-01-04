from time import sleep
from datetime import datetime
from ble_functions import BLE
from flask import Flask, render_template, url_for, request
import plotly.express as px

mac_address = "24:0A:C4:62:52:FE" # Andreas dev board
#mac_address = "7C:9E:BD:66:5B:02" # ESP32 marked "E"

ble = BLE(mac_address)

app = Flask(__name__)
csv_path = './records'
sliderValue = 60
connected = False

def plot_img(df):
       
       fig = px.scatter(df, x='time', y=['vl', 'vr', 'hl', 'hr'])
       fig.update_layout(template="plotly_dark")
       fig.update_layout(plot_bgcolor="#495057", paper_bgcolor="#212529")
       fig.to_image(format='png')
       fig.write_image("static/images/plot.png")

@app.route('/')
def index():
       return render_template("index.html")

@app.route('/get_time', methods=['POST','GET'])
def get_time():
       global sliderValue
       sliderValue = int(request.json['rangeSliderValue'])
       return "get_time"

@app.route('/start', methods=['POST','GET'])
def startRec():

       print("Start")
       connected = ble.connect()
       
       if connected:
              try:

                     ble.start_record()
                     sleep(sliderValue)
                     print("Time ended")
                     ble.stop_record()
                     ble.df.to_csv(f'{csv_path}/{datetime.now()}_ok.csv', sep=',', index=None)
                     plot_img(ble.df)
                     

              except Exception as e:
                     print(e)

                     try:
                            ble.stop_record()
                            ble.df.to_csv(f'{csv_path}/{datetime.now()}_earlystop.csv', sep=',', index=None)
                            plot_img(ble.df)


                     except Exception as e:
                            print(e)
              finally:
              
                     return ble.df.to_json()
     
       return "0"

@app.route('/stop', methods=['POST','GET'])
def stopRec():

       print("Stop")

       try:
              ble.stop_record()
              ble.df.to_csv(f'{csv_path}/{datetime.now()}_stopped.csv', sep=',', index=None)
              plot_img(ble.df)

              return ble.df.to_json()

       except Exception as e:
              print(e)


       return "0"
       

if __name__ == "__main__":
       app.run(debug=True)