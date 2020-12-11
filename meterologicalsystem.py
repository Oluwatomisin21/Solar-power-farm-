import pandas as pd
import numpy as np
import datetime


def mtime(times,flag):
    '''The function generates timestamps for simulation. It takes in the previous timestamp and flag
       to indicate if program just starting 
       
       Inputs:
       times      = Previous  timestamp
       flag       = Status of program

       Outputs:
       times      = A list containing current timestam and flag
       
       '''      
    start=datetime.datetime.now()
    if flag==0:
        times=start
        flag=1
    else:
        times=times + pd.to_timedelta(1,unit='H')
    output=[times,flag]
    return output
    
def mHo(output):
    '''This function generates irradiance incidence on a horizontal surface

       Inputs:
       output        = A list containing current timestam and flag
       
       Outputs:
       Ho         = Irradiance incidence on a flat surface
       
       '''      
    hour=output.hour
    
    if hour<5 or hour > 19:
        Ho=0
    elif hour==6 or hour == 18:
        Ho=100+np.random.uniform(-50,20)
    elif hour==5 or hour == 19:
        Ho=10 +np.random.uniform(-2,2)
    else:
        Ho=1000+np.random.uniform(-300,200)
    return Ho
