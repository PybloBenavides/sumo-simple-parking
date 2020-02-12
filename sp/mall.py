'''
@author: PybloBenavides
@ programmingandmodelling.com

Parking logic in a mall.
Mall has X Parking zones, which are connected.
Vehicles enter the mall when there are available parking spots
if vehicles inside < parking capacity
Each vehicle has a zoning preference ( parking closer to the shop or to exit or ...)
Vehicles go to their zones as desired, if they don't see a parking spot once they are there,
they go to their next preferred zone.
Vehicle inside one zone sees all the parking spots in that zone. 
'''

import os,sys
import sumocfg
import traci
import random

from sumolib import checkBinary

sumoBinary = checkBinary('sumo-gui')

sumoCmd = [sumoBinary, '-c', os.path.join(sumocfg.networks, r"mall\mall.sumocfg")]


PARKING_ENTRANCE = 'networkEntrance'

vehicle_handler = None
rerouted_parkers = None
parking_mall = None
class ParkingMall():
	def __init__(self):
		self.zones = {}
		self.capacity = 0
		self.vehicles_inside = 0
	def add_zone(self, zone):
		self.zones[zone.name] = zone
	def set_capacity(self):
		for zone in self.zones.keys():
			self.capacity += len(self.zones[zone].parking_spots)
		print(f"capacity: {self.capacity}")
	def vehicle_enters(self): 
		self.vehicles_inside += 1
	def vehicle_leaves(self):
		self. vehicles_inside -= 1
	def is_full(self):
		return self.vehicles_inside == self.capacity
	

class ParkingZone():

	def __init__(self, name):
		self.name = name
		self.parking_spots = {}
		self.entrances = []	
	def add_parking_spot(self, name):
		self.parking_spots[name] = None	
	def __str__(self):
		return self.name

class Parker():
	def __init__(self, name, parking_mall):
		self.name = name
		zoneA = parking_mall.zones['A']
		zoneB = parking_mall.zones['B']
		self.parking_preference = [zoneA,zoneB] if random.randint(0,10) > 3 else [zoneB, zoneA]

	def __str__(self):
		return self.name

def store_parking_lots(traci):
	global parking_mall
	parking_mall = ParkingMall()
	for edge in traci.edge.getIDList():
		if 'P_' in edge:
			parkingspot = edge
			zone = parkingspot.split("_")[1]
			if zone not in parking_mall.zones:
				parking_zone = ParkingZone( zone )
				
				parking_mall.add_zone( parking_zone )
			parking_mall.zones[zone].add_parking_spot( parkingspot )
	parking_mall.set_capacity()
	parking_mall.zones['A'].entrances = ['A_Entrance_0', 'A_Entrance_1']
	parking_mall.zones['B'].entrances = ['B_Entrance_0']

def reroute_to_parking_zone( parker ):
	global vehicle_handler, parking_mall
	desired_zone = parker.parking_preference[0]
	vehicle_handler.changeTarget( parker.name, desired_zone.entrances[0] )
	#TODO: Change entrances[0] to shortest path entrance

def apply_parking_logic( parking_entrance ):
	global vehicle_handler, rerouted_parkers, parking_mall
	if not parking_mall.is_full():
		for vehicle in vehicle_handler.getIDList():
			current_edge = vehicle_handler.getRoadID( vehicle )
			if current_edge == parking_entrance and vehicle not in rerouted_parkers.keys():
				parker = Parker(vehicle, parking_mall)
				print(f"tony parker preference {parker.parking_preference}")
				reroute_to_parking_zone(parker)
				rerouted_parkers[vehicle] = parker




def simulate():
	global rerouted_parkers, vehicle_handler
	rerouted_parkers = {}
	traci.start( sumoCmd )
	store_parking_lots( traci )
	step = 0
	vehicle_handler = traci.vehicle
	# rerouted_parkers = []
	while step < 1000:
		traci.simulationStep()
		apply_parking_logic( PARKING_ENTRANCE )
		#Your code
		step += 1
	traci.close()


simulate()