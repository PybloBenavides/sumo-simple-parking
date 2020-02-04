import os,sys
import sumocfg
import traci
import random

from sumolib import checkBinary

sumoBinary = checkBinary('sumo-gui')

sumoCmd = [sumoBinary, '-c', os.path.join(sumocfg.networks, r"mall\mall.sumocfg")]


class ParkingMall():
	def __init__(self):
		self.zones = {}
	def add_zone(self, zone):
		self.zones[zone.name] = zone

class ParkingZone():
	def __init__(self, name):
		self.name = name
		self.parking_spots = {}
	def add_parking_spot(self, name):
		self.parking_spots[name] = None

	def __str__(self):
		return self.name


def store_parking_lots(traci):
	parking_mall = ParkingMall()
	for edge in traci.edge.getIDList():
		if 'P_' in edge:
			parkingspot = edge
			zone = parkingspot.split("_")[1]
			if zone not in parking_mall.zones:
				parking_zone = ParkingZone( zone )
				
				parking_mall.add_zone( parking_zone )
			parking_mall.zones[zone].add_parking_spot( parkingspot )
				
	for zone in parking_mall.zones:
		print(zone)
		print(parking_mall.zones[zone].parking_spots)
		print("..")


def simulate():
	traci.start( sumoCmd )
	store_parking_lots( traci )
	step = 0
	# rerouted_vehs = []
	while step < 1000:
		traci.simulationStep()
		#Your code
		step += 1
	traci.close()


simulate()