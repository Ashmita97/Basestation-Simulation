# Basestation-Simulation
Simulation of a 3-sectored basestation in Python 
For the Final Project for ENTS 656 we had to create a simulation of the downlink behavior of a 3-sectored base station along a road. The base station is oriented in such a manner that one sector(alpha) faces North and the other two sectors face South-East(beta) and South-West(gamma) from the alpha sector. Each sector is separated from the other at an angle of 120°. Since the road along which we have to track our simulation is 20 km West of the base station, the alpha and beta sectors would be the only two sectors having a big enough signal strength to be able to handle any calls along the road.

In general, we are provided with some variable parameters like length of the road, simulation time, number of users, etc. We are also provided with the constant values for certain factors like the height of the base station, transmitter power, number of traffic channels, call rate, etc. Given all these variables and constants we had to write functions in Python to calculate the values of the following to successfully implement the simulation of the final project:

•	Propagation loss using the Okamura-Hata Model 
•	Shadowing using normal distribution library in python 
•	Fading using a Rayleigh distribution library in python
•	EIRP at each sector which was found by subtracting the antenna discrimination from the EIRP at boresight for each sector
•	Total Path loss which was simply Propagation Loss – Shadowing – Fading 
•	RSL at the mobile which was calculated as EIRP – Total Path Loss 
•	Determining whether a user is making a call based on the probability of 2 calls per hour 
•	Determining the initial location of a user/mobile by assuming they are uniformly distributed along the road 
•	Determine the length of each call given that the average call goes on for 3 minutes 
•	Determine if a user is travelling north or south

After calculating all the above along with a few more values we had to setup the specifics of the simulation to handle cases like handoffs, dropped calls due to signal strength, blocked calls due to capacity, adding a new user on the system, deleting an active user from the system, etc. After completing these details our 3-sectored base station simulation was ready to handle calls for users traveling along a road next to to the base station. We then analyzed its behavior under certain circumstances like increased length of road or increased number of users and recorded its behavior in the following parts. 
