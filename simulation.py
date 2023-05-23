#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 27 21:35:16 2020

@author: Ashmita
"""
import functions
import variables
import numpy as np
import json
import sys

# 
updateData = False
simFileLocation = "./extras/simData.js"
userFileLocation = "./extras/userData.js"

if len(sys.argv) > 1:
    if str(sys.argv[1]) == '-u':
        updateData = True

if updateData:
    with open(simFileLocation, "w") as f:
        f.write("var simData = [\n")
    with open(userFileLocation, "w") as f:
        f.write("var userData = [\n")

'''
function to update the given element of the given sector of the sectorTable by the update value mentioned
'''
def updateSectorTable(sector, element, update):
    num = sectorTable.get(sector).get(element)
    num += update
    sectorTable[sector][element] = num

    return None
'''
function to display the contents of the sector table in a more readable manner at intervals of every one hour
'''
def generateReport(hour):
    print("The results after {} hours of simulation are as follows : ".format(hour))
    for sector in sectorTable:
        print("{} Sector :".format(sector))
        print ("{:<30} {:<18}".format('Number of channels currently in use:',sectorTable.get(sector).get('CurrentChannels')))
        print ("{:<30} {:<18}".format('Number of call attempts:',sectorTable.get(sector).get('CallAttempt')))
        print ("{:<30} {:<18}".format('Number of successful calls:',sectorTable.get(sector).get('SuccessfulCalls')))
        print ("{:<30} {:<18}".format('Number of handoff attempts:',sectorTable.get(sector).get('HandOffAttempt')))
        print ("{:<30} {:<18}".format('Number of successful handoffs:',sectorTable.get(sector).get('SuccessfulHandOff')))
        print ("{:<30} {:<18}".format('Number of handoff failures:',sectorTable.get(sector).get('HandOffFailure')))
        print ("{:<30} {:<18}".format('Number of call drops due to low signal strength:',sectorTable.get(sector).get('DCsignal')))
        print ("{:<30} {:<18}".format('Number of call drops due to capacity:',sectorTable.get(sector).get('DCcapacity')))
        print ("{:<30} {:<18}".format('Number of blocked calls due to capacity:',sectorTable.get(sector).get('BCcapacity')))
        print('\n')

#initializing the global variables in the variables file
variables.init()

#creating a list of all 160 users with initially no call up i.e. there are no active users
global Users
Users = []
for i in range(variables.numUsers):
    Users.append([i, 'inactive'])

#creating a dictionary for active Users
global activeUsers
activeUsers = {}

#creating a dictionary for alpha and beta sector for maintaining call statistics
global sectorTable
sectorTable = {'Alpha' : {'DCsignal' : 0,
                          'DCcapacity': 0,
                          'BCcapacity':0,
                          'SuccessfulCalls' : 0,
                          'HandOffAttempt': 0,
                          'SuccessfulHandOff' : 0,
                          'HandOffFailure' : 0,
                          'CurrentChannels' : 0,
                          'CallAttempt' : 0
                          },
               'Beta' :  {'DCsignal' : 0,
                          'DCcapacity': 0,
                          'BCcapacity':0,
                          'SuccessfulCalls' : 0,
                          'HandOffAttempt': 0,
                          'SuccessfulHandOff' : 0,
                          'HandOffFailure' : 0,
                          'CurrentChannels' : 0,
                          'CallAttempt' : 0
                          }
               }
#call to numpy.random.seed function to generate the same random numbers every time
#np.random.seed(0)

#initialising shadowing values for the road
global shadowSample
shadowSample = functions.shadowing_init()

# --------------------BEGINNING SIMULATION---------------------------
#starting to loop through Users to determine if they have an active call and take actions accordingly
for t in range(0, variables.totalTime*3600+1 , variables.timeStep):

    # We will now loop through Users according to priority of active users and so we will sort based on status of active or inactive
    # This will allow us to serve the active members first and then the inactive users
    Users = sorted(Users, key = lambda x: x[1])

    for i in range(variables.numUsers):

        #checking to see if the user has a call up or is inactive
        status = Users[i][1]

        #--------------CASE 1 : FOR USER THAT DOES NOT HAVE CALL UP---------------
        if status == 'inactive':
            #checking the probability of user making a call
            prob = functions.makeCall()

            #when user is not making a call we move on to next user
            if prob == False:
                continue

            #when user does make a call request
            # ------i)  determine user's location along the road
            initialLocation = functions.getInitialLocation()

            # ------ii) determine user's direction along the road i.e. North or South
            direction = functions.getDirection()

            # ------iii) Find RSL at mobile from each sector
            #RSL at the alpha and beta sector
            RSLAlpha = functions.RSL('Alpha', initialLocation, shadowSample)
            RSLBeta = functions.RSL('Beta', initialLocation, shadowSample)

            if RSLAlpha > RSLBeta:
                servingSector = 'Alpha'
                RSLServer = RSLAlpha
                RSLAlternate = RSLBeta
                altSector = 'Beta'
            else:
                servingSector = 'Beta'
                RSLServer = RSLBeta
                RSLAlternate = RSLAlpha
                altSector = 'Alpha'

            #Update sector table to record a call attempt
            updateSectorTable(servingSector,'CallAttempt', 1)

            # -------iv) Determine if RSL from the serving sector is greter that or equal to threshold
            if RSLServer < variables.RSLThresh:
                #When the call attempt fails due to signal strength not being strong enough
                updateSectorTable(servingSector,'DCsignal', 1)
                #we now move on to the next user
                continue
            # -------v) When the call attempt is succesful as the RSL is greater than the threshold we attempt to establish call
            if sectorTable.get(servingSector).get('CurrentChannels') >= variables.numChannel:
                #When there is no available channel it is a blocked call due to capacity
                updateSectorTable(servingSector,'BCcapacity', 1)

                # We try to check for availability in the other sector
                if RSLAlternate < variables.RSLThresh or sectorTable.get(altSector).get('CurrentChannels') >= variables.numChannel:
                    # 2) The other sector is also incapable of handling the call so we move on to the next user
                    updateSectorTable(servingSector,'DCcapacity', 1)
                    continue
                else:
                    # 1) Setting the serving sector and RSL server to the other sector as this sector will try to establish call
                    #updateSectorTable(servingSector,'CallAttempt', -1)
                    servingSector = altSector
                    RSLServer = RSLAlternate
                    updateSectorTable(servingSector,'CallAttempt', 1)

            # -------vi) When RSLServer > RSLThresh and there is an available channel
            #we update the num the number of channels occupied in the right sector
            updateSectorTable(servingSector,'CurrentChannels', 1)

            #add user into the activeUsers directory
            activeUsers[Users[i][0]] =  {'location': initialLocation,
                                         'direction': direction,
                                         'servingSector' : servingSector,
                                         'servingRSL' : RSLServer,
                                         'callTimeLeft': functions.lengthCall()
                                         }

            #change the status of this user to active
            Users[i][1] = 'active'
            continue
            #--------------------------------------END OF CASE 1-------------------------------------------------------

        #--------------CASE 2 : FOR USER THAT DOES HAVE ACTIVE CALL--------------
        elif status == 'active':
            currentUser = activeUsers.get(Users[i][0])
            servingSector = currentUser.get('servingSector')

            #--------- a) Update the user's location
            currentLocation = functions.getCurrentLocation(currentUser.get('location'), currentUser.get('direction'))
            currentUser.update({'location': currentLocation })

            #--------- b) Update the call time
            updatedCallTime = functions.getCallTime(currentUser.get('callTimeLeft'))
            #checking to see if the updated call time is in the limit or the call time has run out
            if updatedCallTime <= 0:
                #call timer has run out so we remove user from activeUser list and free a channel in the servingSector

                updateSectorTable(servingSector,'CurrentChannels', -1)
                #mark as a successful call in that particular sector
                updateSectorTable(servingSector,'SuccessfulCalls', 1)

                #removing active user from the list of active users
                del activeUsers[Users[i][0]]

                #update Users list to mark user as inactive
                Users[i][1] = 'inactive'

                #we are done with this user for now
                continue
            else:
                #call timer has not run out so we simply update amount of time left
                currentUser.update({'callTimeLeft': updatedCallTime})

            #--------- c) Check the bounds of the user's location to see if they have moved beyond ends of roads
            if currentLocation > (variables.roadLength*1000)/2 or currentLocation < -((variables.roadLength*1000)/2) :
                #the user is out of bounds and hence we record this as a successful call and free user and channel
                updateSectorTable(servingSector,'CurrentChannels', -1)

                #mark as a successful call in that particular sector
                updateSectorTable(servingSector,'SuccessfulCalls', 1)

                #removing active user from the list of active users
                del activeUsers[Users[i][0]]

                #update Users list to mark user as inactive
                Users[i][1] = 'inactive'

                continue
            #--------- d) Calculate new RSLServer at new location
            RSLServer = functions.RSL(servingSector, currentLocation, shadowSample)

            #Determine if RSL from the serving sector is greter than or equal to threshold
            if RSLServer < variables.RSLThresh:
                #When the call attempt fails due to signal strength not being strong enough
                updateSectorTable(servingSector,'DCsignal', 1)

                #call has dropped so we remove user from activeUser list and free a channel in the servingSector
                updateSectorTable(servingSector,'CurrentChannels', -1)

                #removing active user from the list of active users
                del activeUsers[Users[i][0]]

                #update Users list to mark user as inactive
                Users[i][1] = 'inactive'

                #we now move on to the next user
                continue
            #---------- e) RSLServer >= RSLThresh we will attempt a handoff
            #compute RSL for the other sector
            if servingSector == 'Alpha':
                altSector = 'Beta'
            else:
                altSector = 'Alpha'

            #RSL at the other sector
            RSLAlt = functions.RSL(altSector, currentLocation, shadowSample)

            if RSLAlt > RSLServer + variables.handOff:
                #There is a potential handoff
                #------i) Recording this as hand-off attempt for the original sector
                updateSectorTable(servingSector,'HandOffAttempt', 1)

                #------ii) Checking if there are sectors available for handoff in the other channel
                if sectorTable.get(altSector).get('CurrentChannels') < variables.numChannel:
                    #There will be a handoff
                    updateSectorTable(servingSector,'SuccessfulHandOff', 1)

                    #The other sector becomes the new serving sector so change activeUser entry
                    currentUser.update({'servingSector': altSector})
                    currentUser.update({'servingRSL': RSLAlt})

                    #Free a channel in the old sector
                    updateSectorTable(servingSector,'CurrentChannels', -1)

                    #Occupy a channel in new sector
                    updateSectorTable(altSector,'CurrentChannels', 1)

                    continue
                else:
                    #There is no channel available in the other sector and so will be recorded as HandOff Failure for old sector
                    updateSectorTable(servingSector,'HandOffFailure', 1)
                    
                    #call will not drop so we simply move on to the next user and try again in the next time step
                    continue
            else:
                 currentUser.update({'servingSector': servingSector})
                 currentUser.update({'servingRSL': RSLServer})
                #--------------------------------------END OF CASE 2-------------------------------------------------------
    #Generating a report after every one hour of simulation
    if t%3600 == 0:
        generateReport(int(t/3600))
    if updateData:
        usrMsg = json.dumps(activeUsers)+','
        if t==variables.totalTime*3600:
            usrMsg = usrMsg[:-1]+"]"
        with open(userFileLocation, "a") as f:
            f.write(usrMsg)
        with open(simFileLocation, "a") as f:
            line = "["
            for sector in sectorTable:
                line += "["
                line += str(sectorTable.get(sector).get('CallAttempt'))+','
                line += str(sectorTable.get(sector).get('SuccessfulCalls'))+','
                line += str(sectorTable.get(sector).get('HandOffAttempt'))+','
                line += str(sectorTable.get(sector).get('SuccessfulHandOff'))+','
                line += str(sectorTable.get(sector).get('HandOffFailure'))
                line += "],"
            line = line[:-1]+"],"
            f.write(line)

if updateData:
    with open(simFileLocation, "a") as f:
        f.write("];var hours = "+str(variables.totalTime)+"; var users = "+str(variables.numUsers)+"; var length = "+str(variables.roadLength)+";")

