from time import sleep
from datetime import datetime
from ble import BLE
from flask import Flask, render_template, url_for, request, send_from_directory, jsonify
import plotly.express as px
import os
import pandas as pd

CSV_PATH = 'records'

mac_address = "24:0A:C4:62:52:FE" # Andreas dev board
#mac_address = "7C:9E:BD:66:5B:02" # ESP32 marked "E"

ble = BLE(mac_address)
app = Flask(__name__)
#app.config["CLIENT_CSV"] = CSV_PATH

sliderValue = 30
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

@app.route('/get-files')
def get_files():
  # Get the list of file names in the folder
  file_names = os.listdir(CSV_PATH)
  
  # Create a list of File objects containing the file names and paths
  files = []
  for file_name in file_names:
    file_path = f'{CSV_PATH}/' + file_name
    file = {'name': file_name, 'path': file_path}
    files.append(file)
  
  # Return the list of files as a JSON response
  return jsonify(files)

@app.route('/records/<path:path>',methods = ['GET','POST'])
def download(path):

    """Download a file."""

    try:
        return send_from_directory(CSV_PATH, path, as_attachment=True)
    except FileNotFoundError:

        print("404")

@app.route('/get_time', methods=['POST','GET'])
def get_time():
       global sliderValue
       sliderValue = int(request.json['rangeSliderValue'])
       return "get_time"

@app.route('/start', methods=['POST','GET'])
def startRec():

       filename = ""
       print("Start")
       filename = f'{CSV_PATH}/{datetime.now()}_ok.csv'

       connected = ble.connect()
       
       if connected:
              try:

                     ble.start_record(sliderValue, filename)
                     sleep(sliderValue)
                     print("Time ended")
                     ble.stop_record()
                     ble.df = pd.DataFrame(ble.data, columns=['time','vl','vr','hl','hr'])
                     ble.df.to_csv(filename, sep=',' , index=None)
                     plot_img(ble.df)
                     

              except Exception as e:
                     print(e)

                     try:
                            ble.stop_record()
                            #ble.df.to_csv(f'{CSV_PATH}/{datetime.now()}_earlystop.csv', sep=',', index=None)
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
              ble.df.to_csv(f'{CSV_PATH}/{datetime.now()}_stopped.csv', sep=',', index=None)
              plot_img(ble.df)
              return ble.df.to_json()

       except Exception as e:
              print(e)

       return "0"

@app.route('/delete', methods=['POST','GET'])
def deleteFiles():

       file_names = os.listdir(CSV_PATH)
  
       for file_name in file_names:
                file_path = f'{CSV_PATH}/' + file_name
                os.remove(file_path)
                print(f"Deleted file: {file_path}")

       return "0"
       

if __name__ == "__main__":
       app.run(debug=True)
