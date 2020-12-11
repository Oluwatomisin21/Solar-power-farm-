from flask import Flask, jsonify, request
import pandas as pd
import numpy as np
import datetime
import pickle
import utils
import xgboost as xgb

app = Flask(__name__)


@app.route("/digitaltwin", methods=['GET'])
def digitaltwin():
    '''The digital twin is an API that takes in meterological inputs and predicts
       the best operating conditions. It consists of four layers:
       
       Layers:
       1. Data Preparation Layer
       2. Machine Learning Layer
       3. Twin Optimization Layer
       4. Data Presentation Layer
       
       Inputs:
       Ho         = Irradiance incidence on a flat surface
       date_time  = Current date and time
       
       Outputs:
       optimal_conditions = Optimal operating condition
       
       '''  
    date_time=request.args.get('date_time')
    
    Ho=float(request.args.get('Ho'))
    
    # Data Preparation Layer
    model_input=data_prep(Ho,date_time)
    
    #Machine Learning layer physical asset
    digital_model = pickle.load(open('digital_model.sav', 'rb'))
    Ht = digital_model.predict(model_input)     # Prediction of Tilted Irradiance
    Power=utils.pv_power(Ht)                    # Get Solar PV Electrical Power    
    
    data=model_input
    data['Ht']=Ht
    data['P']=Power
    data['date_time']=date_time
    
    # Optimization Layer
    optimal_data=optimization(data)
    
    
    # Data Presentation Layer
    optimal_data.drop(['N','H'],axis=1,inplace=True);
    optimal_data_dict=optimal_data.to_dict(orient='records')              
    return jsonify(optimal_data_dict)

# Twin Optimization Layer
def optimization(data):
    '''The optimization layer finds the optimal operating coditions 
       for the solar PV digital ML asset
       
       Inputs:
       data               = All Predicted Scenarios from ML asset
       
       Outputs:
       optimal_conditions = Optimal operating condition
       
       '''
    return data[data.Ht==data.Ht.max()].head(1)

# Data Preparation Layer
def data_prep(Ho,date_time):
    '''The data preparation layer converts meterological inputs from weather api to inputs
       suitable to machine learning layer
       Inputs:
       Ho         = Irradiance incidence on a flat surface
       latitude   = Latitude of location
       date_time  = Current date and time
       
       Outputs:
       optimal_conditions = Optimal operating condition
       
       '''    
    
    # Convert the time to suitable values
    date_time=pd.to_datetime(date_time)
    date_time=pd.Series(date_time)
    H=date_time.dt.hour
    N=date_time.dt.dayofyear
    
    # Create Values for tilt and azimuth
    B=np.arange(0,90.5,5)
    Zs=np.arange(-90,90.5,5)

    # Meshgrid to pair values
    B,Zs=np.meshgrid(B,Zs)

    # Flatten meshgrid
    B=B.flatten()
    Zs=Zs.flatten()
    
    Ho=list(np.repeat(Ho,703))
    N=list(np.repeat(N,703))
    H=list(np.repeat(H,703))
    
    # Define model inputs
    dict={'N':[],'H':[],'Azimuth':[],'Tilt':[],'Ho':[]}
	
    dict['N']=N
    dict['H']=H
    dict['Ho']=Ho
    dict['Tilt']=B
    dict['Azimuth']=Zs
    
    data=pd.DataFrame.from_dict(dict)
    
    return data
    
if __name__ == '__main__':
    app.run(port=5002, debug=True)