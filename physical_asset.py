import pandas as pd
import datetime
import utils

def physicalasset(lat,Zs,B,datetime,Ho):
    '''The physcial asset is a mathematical model that takes in meterological inputs 
       and calculates the power output of the solar pv. It consists of three layers:
       
       Layers:
       1. Data Preparation Layer
       2. Mathematical Model Layer
       3. Data Presentation Layer
       
       Inputs:
       lat        = Latitude
       B          = Tilt angle
       Zs         = Azimuth angle
       date_time  = Current date and time
       Ho         = Irradiance incidence on a flat surface
       
       Outputs:
       data       = Output of physical asset
       
       '''      
    
    # Data Preparation Layer
    # Converts date_time to Y,M,D,H,m
    date_time=pd.to_datetime(datetime)
    date_time=pd.Series(date_time)
    day=date_time.dt.day
    hour=date_time.dt.hour
    year=date_time.dt.year
    month=date_time.dt.month
    minutes=date_time.dt.minute
    
    # Mathematical Model Layer
    N=date_time.dt.dayofyear                            # solar day
    d_ang=utils.d_angle(N)                              # declination angle
    h_ang=utils.h_angle(N,hour,minutes)                   # hour angle
    theta=utils.theta_angle(Zs,B,lat,N,hour,minutes)    # incidence angle
    phi=utils.phi_angle(lat,N,hour,minutes)             # solar angle
    Ht=utils.titled_radiation(Ho,theta,phi)             # irradinace on tilted surface
    power=utils.pv_power(Ht)                            # power 
    
    # Data Presentation Layer
    dict={'date_time':[],'Azimuth':[],'Tilt':[],'Ho':[],'Ht':[],'P':[]}

 
    dict['Ho']=Ho
    dict['Ht']=Ht
    dict['Tilt']=B
    dict['Azimuth']=Zs
    dict['P']=power
    dict['date_time']=datetime
    
    data=pd.DataFrame.from_dict(dict)
    return data
