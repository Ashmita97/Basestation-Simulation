#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 24 12:30:33 2020

@author: Ashmita
#check loaction of user at every second and then 
"""
import numpy as np
import variables 
import math
import random

'''
function to convert a linear value to dB
'''
def linearToDb(linearVal):
    # factor is usually 1 but can change depending on situation
    dBvalue = 10*np.log10(linearVal)
    return dBvalue
    
'''
function to calculate the propagation loss using the Okamura-Hata model
'''
def propagationLoss(sector, currLocation):
    #initialising value of f according to prop
    if sector == 'Alpha':
        f = variables.frequencies[0]
    elif sector == 'Beta':
        f = variables.frequencies[1]
    #we divide the distane calculated from the basestation with 1000 to get the distance in kms     
    distance = mobileBasestationDist(currLocation)/1000
    #propagation loss caused due to the mobile height 
    mobileLoss = (1.1 * np.log10(f) - 0.7)*variables.mobileHeight - (1.56*np.log10(f) - 0.8)
    
    #total propagation loss at transmitter 
    pL = 69.55 + 26.16*np.log10(f) - 13.82*np.log10(variables.baseHeight) + (44.9 - 6.55*np.log10(variables.baseHeight))*np.log10(distance) - mobileLoss
    
    return pL

'''
function to calculate the shadowing which is same for all sectors and has a 
log-normal distribution with a zero mean and sigma = 2 dB 
'''
def shadowing_init():
    # zero mean 
    size = int((variables.roadLength*1000/10)) #we are told to calculte shadowing at every 10m 
    mean = 0
    # standard deviation is 2 dB
    sigma = 2 #in dB
    
    #using np.random.normal to calcalte the log normal distribution of shadowing
    sample = np.random.normal(mean, sigma, size)
    
    return sample
'''
function to return the particular shadowing value based on the current Location of the User
'''
def shadowingValue(currLocation, sample):
    #the currentLocation is the relative location to the basetstation, therefore to find corresponding shadowing value we have to find it's location on the road
    relLoc = (variables.roadLength*1000/2) - currLocation
    
    #currLocation provided to us in meters so when we divide with 10 it should give us the index of the right shadowing value 
    index = int(relLoc/10)
    #special case when the user is at the southmost bound
    if(relLoc == variables.roadLength*1000):
        index = int(relLoc/10) - 1
       
    return sample[index]

'''
function to calculate fading using a Rayleigh distribution with zero mean and 
unit variance
It will be different for the two different sectors
'''
def fading():
    num_samples = 10
    variance = 1
    #using the built in function rayleigh distribute 10 samples
    mag = np.random.rayleigh(variance,num_samples)
    
    linear_z = []
    for i in range(num_samples):
        linear_z.append(linearToDb(mag[i]**2))
        
    #sorting the array of Rayleigh Samples generated in ascending order to get deepest fades
    linear_z.sort()
    
    #Taking the second deepest fade, so throwing away the first deepest fade and returning its value in dB 
    return linear_z
'''
function to calculate the EIRP from the basestation to any particular point on
the antenna 
'''
def EIRP(currLocation, sector):
    #calculate EIRP at boresight which is directly in front of antenna
    EIRPatBore = variables.P_Tx - variables.lineLoss + variables.antennaGain
    
    #Calculate the distance of the mobile from the basestation based on current location
    distanceFromMobile = mobileBasestationDist(currLocation)
    
    baseLocation_y = currLocation 
    #creating a vector for the distance betwen a 
    vectorV = [variables.baseLocation_x,baseLocation_y]

    #creating a unit vector in the direction the antenna is pointing based on which sector we are in
    if sector == 'Alpha':
        vectorU = [0,1]
    elif sector == 'Beta':
        vectorU = [math.sqrt(3)/2, -1/2]
        
    # calculate the magnitude of the unit vector   
    unitMag = math.sqrt(vectorU[0]**2 + vectorU[1]**2)
    
    #calculate the angle off of boresight or the angle between the two vectors in radians
    theta_rad = np.arccos((vectorU[0]*vectorV[0] + vectorU[1]*vectorV[1])/(distanceFromMobile*unitMag))
    
    #converting thetha i radians to theta in degrees
    theta_deg = int(np.round(np.degrees(theta_rad)))
    
    anteDiscrim = antennaDiscrimination(str(theta_deg))
    finalEIRP = EIRPatBore - float(anteDiscrim)
    
    return finalEIRP

'''
function to return the antenna discrimination based on the information provided in 
antenna_pattern.txt, according to the angle provided theta
'''   
def antennaDiscrimination(theta):
    #using open file method to read all the line in the file antenna_pattern.txt
    file = open("antenna_pattern.txt").readlines()
    
    #iterarting through each line in the file to find a match for theta
    for line in file:
        if theta in line:
            val = line.split('\t')
            break
    
    #return the antenna discrimination value for matching theta 
    return val[1].rstrip() 

'''
function  to calculate the distance between the mobile and the basestation based 
upon the current location of the car
'''    
def mobileBasestationDist(currLocation):
    #currentLocation is provided in meters so we subtract 300m (location of the basestation) 
    #and take its absolute value to get the distance between the mobile and basestation on the road
    
    #to calculate the diagonal distance between the basestation and the mobile we use Pythagoras Theorem
    distMobileBase = math.sqrt(currLocation**2 + variables.baseLocation_x**2)
    
    return distMobileBase

'''
function to calculate the received signal level at the mobile
'''
def RSL(sector, currentLocation, shadowSample):
    # the total path loss
    
    #calculate total propagation loss using the Okamura Hata model
    propLoss = propagationLoss(sector, currentLocation)
            
    #get the shadowing value according to the current location
    shadow = shadowingValue(currentLocation, shadowSample)
            
    #fading values for the alpha and beta sector
    linearVal = fading()
    if sector == 'Alpha':
        fade = linearVal[1]
    else:
        fade = linearVal[2]
            
    #EIRP values for the alpha and beta sectors
    EIRPval = EIRP(currentLocation,sector)
    
    #print("EIRP: ",EIRPval,"prop loss: ", propLoss, "shadow: ", shadow, "fade: ", fade,"loc: ", currentLocation)        
    pathLoss = propLoss - shadow - fade 
    
    # the total recieved signal level 
    RSL = EIRPval - pathLoss 
    
    return RSL
'''
function to determine if each user who does not have an active call is going 
to make a call
'''    
def makeCall():
    totalSeconds = 60*60
    #the probability of making a call every hour
    num = random.randint(1,totalSeconds)
    if (num <= variables.callRate):
        return True
    else:
        return False
       
'''
function to determine the direction the user is travelling in: there is a 50/50 chance that the user is travelling either 
North direction or the South direction
'''
def getDirection():
    dir = random.randrange(-1, 2, 2)
    
    return dir # -1 for South and 1 for North

'''
function to get the initial location of each user. We will use np.random.uniform to generate initial location values that are
uniformly distributed between 0 and 6000 m 
'''
def getInitialLocation():
    loc = np.random.uniform(0, variables.roadLength*1000)

    #The location relative to the basestation which is considered to be the origin
    location =  (variables.roadLength * 1000)/2 - loc
    return location


'''    
function to determine the length of a call. Call lengths will be exponentially distributed so I am using the np.
'''
def lengthCall():
    #finding the call duration in seconds
    callDurSec = variables.callDuration *60
    
    return np.random.exponential(callDurSec)

'''
function to update the user's current ocation given the speed of travel as well as the time step
'''
def getCurrentLocation(initialLocation, direction):
    #calculating the distance travelled in the given time step
    distTravelled = variables.userSpeed * variables.timeStep * direction
    
    #updating location
    currentLocation = initialLocation + distTravelled
    
    return currentLocation

'''
function to update the time left of a call according to time step. When the timer runs out it marks the successful completion of a call
'''
def getCallTime(timeLeft):
    #return the timeLeft minus the timestep given to us
    return timeLeft - variables.timeStep











































      
    