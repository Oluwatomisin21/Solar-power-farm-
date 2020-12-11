import utils
import pickle
import numpy as np
import pandas as pd
import physical_asset as ps
from numpy.matlib import repmat as repmat



def digital_asset(Ho):
    '''The digital_asset module takes in meterological inputs and agregates
       the best operating conditions. It consists of four layers:
       
       Layers:
       1. Data Preparation Layer
       2. Machine Learning Layer
       3. Twin Optimization Layer
       4. Agregation  Layer
       
       Inputs:
       Ho         = Irradiance incidence on a flat surface
       
       
       Outputs:
       aggregated_output = Agregated Optimal Energy and Efficiency  
       '''  
    digital_input= data_digital(Ho)
    digital_output=prediction(digital_input)
    optimal_output=optimization(digital_output)
    aggregated_output=aggregation(optimal_output)
    
    return  aggregated_output
    
def physical_asset(Ho,lat,B,Zs):
    '''The physical_asset module takes in meterological inputs,latitude,tilt and time. It agregates
       the energy generated. It consists of three layers::
       
       Layers:
       1. Data Preparation Layer
       2. Mathematical Computation Layer
       3. Agregation Layer
       
       Inputs:
       lat        = Latitude
       B          = Tilt angle
       Zs         = Azimuth angle
       date_time  = Current date and time
       Ho         = Irradiance incidence on a flat surface
       
       Outputs:
       aggregated_output = Agregated Optimal Energy and Efficiency 
       ''' 
    
    # Data Preparation Layer
    Ho=Ho.squeeze()
    date_time=pd.date_range('2017-01-01 00:00:00','2017-12-31 23:00:00',freq='H')
    B=list(np.repeat(B,8760))
    Zs=list(np.repeat(Zs,8760))
    lat=list(np.repeat(lat,8760))
    
    # Mathematical Computation Layer
    physical_output=ps.physicalasset(lat,Zs,B,date_time,Ho)
    physical_output.set_index("date_time",inplace=True)
    
    # Agregation Layer
    aggregated_output=aggregation(physical_output)
    
    return  aggregated_output
    
      
def data_digital(Ho):   
    '''The data digital function converts meterological inputs from weather api to inputs
        suitable to machine learning layer
        Inputs:
        Ho         = Irradiance incidence on a flat surface
       
        Outputs:
        data = DataFrame of ['N','H','Azimuth','Tilt','Ho'] suitable for ML layer    
        '''       
    Ho=list(Ho.values)
    date_time=pd.date_range('2017-01-01 00:00:00','2017-12-31 23:00:00',freq='H')
    
    # Convert the time to suitable values
    date_time=pd.to_datetime(date_time)
    date_time=pd.Series(date_time)
    H=date_time.dt.hour
    N=date_time.dt.dayofyear
 

    # Create Values for tilt and azimuth
    B=np.arange(0,90.5,5)
    Z=np.arange(-90,90.5,5)

    # Meshgrid to pair values
    BB,ZZ=np.meshgrid(B,Z)

    # Flatten meshgrid
    BB=BB.flatten()
    ZZ=ZZ.flatten()

    #Repeat values to align with dimension
    date_time=list(np.repeat(date_time,703))
    Ho=list(np.repeat(Ho,703))
    N=list(np.repeat(N,703))
    H=list(np.repeat(H,703))
    BB=list(repmat(BB,8760,1).flatten())
    ZZ=list(repmat(ZZ,8760,1).flatten())

    # Define model inputs
    dict={'N':[],'H':[],'Azimuth':[],'Tilt':[],'Ho':[]}
    dict['N']=N
    dict['H']=H
    dict['Ho']=Ho
    dict['Tilt']=BB
    dict['Azimuth']=ZZ
    
    data=pd.DataFrame.from_dict(dict)
    data['date_time']=date_time
    return data

def prediction(data):
    '''The prediction module is the ML layer for scoring input data 
       
       Inputs:
       data               = All Predicted Scenarios from ML asset
       
       Outputs:
       optimal_conditions = Optimal operating condition
       
       '''
    date_time=data.date_time
    data.drop('date_time',axis=1,inplace=True)
    digital_model = pickle.load(open('digital_model.sav', 'rb'))
    Ht = digital_model.predict(data)     # Prediction of Tilted Irradiance
    Power=utils.pv_power(Ht)        
    data['Ht']=Ht
    data['P']=Power
    data['date_time']=date_time
    data.drop(['N','H','Tilt','Azimuth'],axis=1,inplace=True)
    data.set_index("date_time",inplace=True)
    
    return data
    
def optimization(data):
    '''The optimization layer finds the optimal operating coditions 
       for the solar PV digital ML asset
       
       Inputs:
       data               = All Predicted Scenarios from ML asset
       
       Outputs:
       optimal_conditions = Optimal operating condition
       
       '''    
    return data.resample('H').max()

def aggregation(data):
    '''The aggregation module samples and sums all houly data as monthly or yearly data 
       Inputs:
       data               = Forecasted houly operating parameters
       
       Outputs:
       data = Dictionary containing the monthly energy and yearly energy produced   
       '''   
    daily_energy= data.resample('D').sum()
    monthly_energy= data.resample('M').sum()
    monthly_energy['mu']= 30*monthly_energy['Ht']/ monthly_energy['Ho']
    monthly_energy['P']=0.001*monthly_energy['P']
    
    yearly_energy=data.resample('Y').sum()
    yearly_energy['mu']=30*yearly_energy['Ht']/yearly_energy['Ho']
    yearly_energy['P']=0.001*yearly_energy['P']    
    
    data={'mpower': list(monthly_energy['P'].round(2)), 'mefficiency': list(monthly_energy['mu'].round(2)),\
          'ypower': list(yearly_energy['P'].round(2)), 'yefficiency': list(yearly_energy['mu'].round(2))}
    return data