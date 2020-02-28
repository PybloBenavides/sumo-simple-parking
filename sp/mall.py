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
NETWORK_EXIT = 'networkExit'
PARKING_EXIT = 'parkingExit'
MIN_PARKING_TIME = 20
MAX_PARKING_TIME = 50

step = 0
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
	def get_free_parking_spots(self):
		count = 0
		for zone in self.zones.values():
			for spot in zone.parking_spots.values():
				if spot is None:
					count += 1
		return count
	

class ParkingZone():

	def __init__(self, name):
		self.name = name
		self.parking_spots = {}
		self.entrances = []	
	def add_parking_spot(self, name):
		self.parking_spots[name] = None	

	def find_parking_spot(self):
		for parking_spot, occupancy in self.parking_spots.items():
			if occupancy is None:
				return parking_spot
		return None
	def reserve_parking_spot(self, parking_spot, parker):
		self.parking_spots[parking_spot] = parker

	def __str__(self):
		return self.name

class Parker():
	def __init__(self, name, parking_mall):
		self.name = name
		zoneA = parking_mall.zones['A']
		zoneB = parking_mall.zones['B']
		self.parking_preference = [zoneA,zoneB] if random.randint(0,10) > 3 else [zoneB, zoneA]
		self.is_parking = False
		self.parking_spot = None
		self.end_parking_time = None
	def park(self):
		self.is_parking = True
	def change_parking_preference(self):
		self.parking_preference = list(reversed(self.parking_preference))
	def choose_parking_spot(self, parking_spot):
		self.parking_spot = parking_spot
	
	def free_parking_spot(self):
		'''
		Frees Parking spot for parker and also Parking zone
		'''
		zone = self.parking_preference[0]
		zone.reserve_parking_spot(self.parking_spot, None)
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
	print(f"rerouting veh {parker.name} to zone entrance {desired_zone.entrances[0]}")
	try:
		vehicle_handler.changeTarget( parker.name, desired_zone.entrances[0] )
	except:
		vehicle_handler.changeTarget( parker.name, desired_zone.entrances[1] )
	#TODO: Change entrances[0] to shortest path entrance

def reroute_to_parking_spot(parker, parking_spot):
	global vehicle_handler, step
	parker.choose_parking_spot(parking_spot)
	vehicle_handler.changeTarget( parker.name, parking_spot )
	print(f"Vehicle {parker.name} going into {parking_spot}")
	parking_duration = random.randint( MIN_PARKING_TIME, MAX_PARKING_TIME )
	vehicle_handler.setStop(parker.name, parking_spot, duration=parking_duration)
	parker.end_parking_time = parking_duration + step
	# parker.set_end_parking_time(parking_duration + step)
	# parkings_occ[parking_spot] = (parker.name, parking_duration + step)

def find_spot_in_zone(parker, parking_zone):
	parking_spot = parking_zone.find_parking_spot()
	if parking_spot is None:
		return None
	parking_zone.reserve_parking_spot(parking_spot, parker)
	reroute_to_parking_spot(parker, parking_spot)
	return parking_spot


def exit_parking( parker ):
	'''
	Make vehicle exit Parking spot and Parking lot.
	'''
	global vehicle_handler, parking_mall
	vehicle_handler.changeTarget( parker.name, NETWORK_EXIT )
	print(f"rerouting {parker.name} to {NETWORK_EXIT}")
	try:
		vehicle_handler.resume(vehicle)
		parker.free_parking_spot()
		parkings_occ[parking_spot] = None
	except:
		return

def apply_parking_logic( parking_entrance, step ):
	global vehicle_handler, rerouted_parkers, parking_mall
	# if not parking_mall.is_full():
	for vehicle in vehicle_handler.getIDList():
		current_edge = vehicle_handler.getRoadID( vehicle )
		if vehicle not in rerouted_parkers:
			if current_edge == parking_entrance and not parking_mall.is_full():
				parker = Parker(vehicle, parking_mall)
				reroute_to_parking_zone(parker)
				rerouted_parkers[vehicle] = parker
				parking_mall.vehicle_enters()
		else:
			parker = rerouted_parkers[vehicle]
			parking_zone = parker.parking_preference[0]
			if current_edge in parking_zone.entrances and parker.parking_spot is None:
				spot = find_spot_in_zone(parker, parking_zone)
				# print("tony parker is in the entrance of its desired zone.")
				if spot is None:
					parker.change_parking_preference()
					reroute_to_parking_zone(parker)
			elif current_edge == parker.parking_spot:
				if not parker.is_parking: # parker just entered parking spot
					parker.park( )
					print(f"{parker.name} is going to start parking ...")
				else:
					if step >= parker.end_parking_time:
						exit_parking(parker)
						print(f"{parker.name} is going to leave the parking ...")
			elif current_edge == PARKING_EXIT:
				parking_mall.vehicle_leaves()
				rerouted_parkers.pop(vehicle)
	print(f"parking mall vehicles inside: {parking_mall.vehicles_inside}")
	free_spots = parking_mall.get_free_parking_spots()
	print(f"free parking spots: {free_spots}")




def simulate():
	global rerouted_parkers, vehicle_handler, step
	rerouted_parkers = {}
	traci.start( sumoCmd )
	store_parking_lots( traci )
	step = 0
	vehicle_handler = traci.vehicle
	# rerouted_parkers = []
	while step < 1000:
		traci.simulationStep()
		apply_parking_logic( PARKING_ENTRANCE, step )
		#Your code
		step += 1
	traci.close()


simulate()