import datetime
import numpy as np

# Get solar day
def solar_day(year,month,day):
    return (datetime.date(year,month,day)-datetime.date(year,1,1)).days 
    

# Source:S A. Kalogirou,(2009) Solar Energy Engineering and Processes,Elsevier

# Solar model calculates the declination angle
# Equation:2.5
def d_angle(N):
    return 23.45*np.sin(np.radians(360*(N+284)/365))
 

 
# Solar model calculates hour angle
# Equation:2.9  
def h_angle(N,hour,minute):
    B=((360/365)*(N-81))
    LSTM=15
    EoT=9.87*np.sin(np.radians(2*B))-7.53*np.cos(np.radians(B))-1.5*np.sin(np.radians(B))
    TC=4*(3.947-LSTM)+EoT
    AST=((hour+minute/60)+(TC/60))
    hangle=(AST-12)*15
    hangle[hangle<0]=180+hangle
    hangle[hangle>0]=180-hangle
    return hangle

      
# Solar model calculates the cosine of the solar incidence angle
# Equation:2.18
def theta_angle(Z,B,lat,N,hour,minutes):
    # B = Panel tilt angle
    # Z = Panel azimuth angle
    # lat = Local Latitude
    # h_ang = hour angle
    # d_ang = Declination angle# theta = incidence angle
    
    d_ang=np.radians(d_angle(N))
    h_ang=np.radians(h_angle(N,hour,minutes))
    lat=np.radians(lat)
    B=np.radians(B)
    Z=np.radians(Z)
    
    theta =   np.sin(lat)*np.sin(d_ang)*np.cos(B) \
            - np.cos(lat)*np.sin(d_ang)*np.sin(B)*np.cos(Z) \
            + np.cos(lat)*np.cos(d_ang)*np.cos(h_ang)*np.cos(B) \
            + np.sin(lat)*np.cos(d_ang)*np.cos(h_ang)*np.sin(B)*np.cos(Z) \
            + np.cos(d_ang)*np.sin(h_ang)*np.sin(B)*np.sin(Z)
    theta=np.degrees(np.arccos(theta))
    theta[theta>90]=180-theta
    return theta
    
    

# Solar model calculates the cosine of the solar alitude angle
# Equation:2.12

def phi_angle(lat,N,hour,minutes):
    
    d_ang=np.radians(d_angle(N))
    h_ang=np.radians(h_angle(N,hour,minutes))
    lat=np.radians(lat)
    phi=np.sin(lat)*np.sin(d_ang)+np.cos(lat)*np.cos(d_ang)*np.cos(h_ang)
    phi=np.degrees(np.arccos(phi))
    phi[phi>90]=180-phi
    return phi
    
    
# Solar model converts radiation on horizontal surface to tilted surface
# Equation:2.88 and 2.89

def titled_radiation(Ho,theta,phi):
    return (np.cos(np.radians(theta))/np.cos(np.radians(phi)))*Ho
    

# PV-model converts irradiance to electric power
# Ayodele, T.R.,Ogunjuyigbe, A.S.O. and Oladeji, S. (2018) ‘Determination of optimal tilt
# angles in some selected cities of Nigeria for maximum extractable solar
# energy’, Int. J. Renewable Energy Technology, Vol. 9, No. 4, pp.453–483
# Source: Equation 10
def pv_power(Ht):
    A=1000
    mu=0.30
    return A*Ht*mu/1000