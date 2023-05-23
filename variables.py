#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 27 20:52:37 2020

@author: Ashmita
"""
def init():
    #basic parameters of the simulation
    global roadLength
    roadLength = 6 #in km
    global timeStep
    timeStep = 1 #in seconds
    global totalTime
    totalTime = 6 #in hours
    
    #Parameters unique to each sector in the basestation
    global baseHeight
    baseHeight = 50 #in meters
    global baseLocation_x #basestation location horizontally from the road
    baseLocation_x = 20 # in m
    global P_Tx
    P_Tx = 43 #in dBm 
    global lineLoss
    lineLoss = 2 #in dB
    global antennaGain
    antennaGain = 14.8 #in dBi
    global numChannel
    numChannel = 15 #number of traffic channels per sector 
    global frequencies
    frequencies = [ 860, 870 ] #in MHz, first is for alpha sector, second for beta sector and so on
    
    #Parameters of the mobile 
    global mobileHeight 
    mobileHeight = 1.5 # in m 
    global handOff # the handoff margin
    handOff = 3 #in dB
    global RSLThresh
    RSLThresh = -102 #in dBm 
    
    #Parameters related to User and calling
    global numUsers #number of Users
    numUsers = 160
    global callRate
    callRate = 2 # calls per hour
    global callDuration
    callDuration = 3 #minutes per call 
    global userSpeed #v
    userSpeed = 15 #m/s 


    
    