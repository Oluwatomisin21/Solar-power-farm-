from flask import Flask, Response, jsonify, request,redirect,render_template
import meterologicalsystem as mt
import physical_asset as ps
import pandas as pd
import requests
import planner
import pickle
import json
import datetime
import time


app = Flask(__name__)

@app.route("/")
def index():
    ''' Html landing page'''
    
    return render_template('index.html')
    
    
 
@app.route("/upload/")
def upload():
    '''Page to upload planning data'''
    
    return render_template('upload.html')  
    
    

@app.route("/business/",methods=['GET','POST'])
def business():
    ''' Endpoint displays the comparison between traditional and twin configuration'''

    return render_template('business.html')



@app.route("/submit_data/",methods=['POST'])
def submit_data():
    ''' Function computes output for digital twin and saves on pickle file'''
    # Upload file and save as file_upload
    file=request.files["file"]
    file.save("file_upload.csv")
    
    # Obtain all values for digital twins
    Ho=pd.read_csv("file_upload.csv")
    twin_output=planner.digital_asset(Ho)
    
    # Save twin_output as a pikle file
    with open("twin_output.pkl","wb") as f:
        pickle.dump(twin_output,f)
    return redirect("/business/")


@app.route('/realtime')
def realtime():
    ''' Realtime server side event initiator'''
    
    return Response(generate_data(),mimetype='text/event-stream')



@app.route("/planning/",methods=['GET','POST'])
def planning():
    '''Planing server side event initiator'''
    try:
        data=request.get_json()
        B=float(data['tilt'])
        Zs=float(data['azimuth'])
    except TypeError:
        B=0
        Zs=0
    lat=7.3775
    
    # Obtain values for the traditional pv system
    Ho=pd.read_csv("file_upload.csv")
    with open("twin_output.pkl","rb") as f:
        twin_output=pickle.load(f)
    traditional=planner.physical_asset(Ho,lat,B,Zs)

    
    # Data Presentation in webpage
    month_label=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    twin_output['month_label']=month_label
    traditional['month_label']=month_label
    data={'twin_output':twin_output,'traditional':traditional}
    data_json=json.dumps(data)
    return jsonify(data_json)
       
    

def generate_data():
    ''' Function used for simulating and plotting realtime data'''
    flag=0
    times=0
        
    while True:
        time.sleep(2)
            
        # Query Meterological Data
        output=mt.mtime(times,flag)
        Ho=int(mt.mHo(output[0]))
        times=output[0]
        flag=output[1]
        meterological_data={'date_time':times,'Ho':Ho}
            
        # Digital Twin Query
        twin_api    =   "http://127.0.0.1:5002/digitaltwin?date_time=" \
                      + str(meterological_data['date_time'].strftime('%Y-%m-%d %H:%M')) \
                      + "&Ho=" + str(meterological_data['Ho'])
            
        twin_output = requests.get(twin_api).json()
        twin_output=twin_output[0]
            
            
        # Physical Asset Query
        physical_output=ps.physicalasset(7.3775,twin_output['Azimuth'],twin_output['Tilt'],\
                                        meterological_data['date_time'].strftime('%Y-%m-%d %H:%M'),\
                                        meterological_data['Ho'])
        physical_output=physical_output.to_dict(orient='records')
        physical_output=physical_output[0]
        twin_output["Pp"]=physical_output["P"]
            
        # Data Presentation in webpage
        data={'twin_output':twin_output,'physical_output':physical_output}
        data_json=json.dumps(data)
        yield f"data:{data_json}\n\n"
    

    
    
if __name__ == '__main__':
    app.run(port=5000, debug=True)