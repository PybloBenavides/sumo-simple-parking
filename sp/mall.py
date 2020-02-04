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


PARKING_ENTRANCE = 'ParkingEntrance'

vehicle_handler = None
rerouted_vehs = None
parking_mall = None
class ParkingMall():
	def __init__(self):
		self.zones = {}
		self.capacity = -1
		self.vehicles_inside = 0
	def add_zone(self, zone):
		self.zones[zone.name] = zone
	def set_capacity(self):
		for zone in self.zones.keys():
			self.capacity += len(self.zones[zone].parking_spots)
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
		
	def add_parking_spot(self, name):
		self.parking_spots[name] = None

	def __str__(self):
		return self.name

class Parker():
	def __init__(self, name):
		self.name = name
		self.parking_preference = ['A','B'] if random.randint(0,10) > 3 else ['B','A']

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
	# for zone in parking_mall.zones:
	# 	print(zone)
	# 	print(parking_mall.zones[zone].parking_spots)
	# 	print("..")

def apply_parking_logic( parking_entrance ):
	global vehicle_handler, rerouted_vehs, parking_mall
	for vehicle in vehicle_handler.getIDList():
		current_edge = vehicle_handler.getRoadID( vehicle )
		if current_edge == parking_entrance and vehicle not in rerouted_vehs:
			if parking_mall.is_full():
				continue
			parker = Parker(vehicle)
			print(f"tony parker preference {parker.parking_preference}")



def simulate():
	global rerouted_vehs, vehicle_handler
	rerouted_vehs = []
	traci.start( sumoCmd )
	store_parking_lots( traci )
	step = 0
	vehicle_handler = traci.vehicle
	# rerouted_vehs = []
	while step < 1000:
		traci.simulationStep()
		apply_parking_logic( PARKING_ENTRANCE )
		#Your code
		step += 1
	traci.close()


simulate()