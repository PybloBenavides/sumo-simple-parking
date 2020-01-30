import os,sys
import sumocfg
import traci
import random

from sumolib import checkBinary

sumoBinary = checkBinary('sumo-gui')

sumoCmd = [sumoBinary, '-c', os.path.join(sumocfg.networks, r"simple_network\simple.sumocfg")]

PARKING_EXIT = 'pExit'
MIN_PARKING_TIME = 15
MAX_PARKING_TIME = 30

parkings_occ = None
vehicle_handler = None
edgeHandler = None
step = None
rerouted_vehs = None


def find_parking_spot():
	global parkings_occ
	for parking, occupancy in parkings_occ.items():
		if occupancy is None:
			return parking
	return None


def reroute_to_parking_spot(vehicle, parking_spot):
	global vehicle_handler, parkings_occ, step
	vehicle_handler.changeTarget(vehicle,parking_spot)
	print(f"Vehicle {vehicle} going into {parking_spot}")
	parking_duration = random.randint( MIN_PARKING_TIME, MAX_PARKING_TIME )
	vehicle_handler.setStop(vehicle, parking_spot, duration=parking_duration)
	parkings_occ[parking_spot] = (vehicle, parking_duration + step)

def exit_parking( vehicle, parking_spot ):
	global parkings_occ
	vehicle_handler.changeTarget( vehicle, PARKING_EXIT )
	print(f"rerouting {vehicle} to {PARKING_EXIT}")
	try:
		vehicle_handler.resume(vehicle)
		parkings_occ[parking_spot] = None
	except:
		return

def apply_parking_logic():
	global vehicle_handler, parkings_occ, step, rerouted_vehs
	for vehicle in vehicle_handler.getIDList():
		current_edge = vehicle_handler.getRoadID( vehicle )
		if current_edge == 'pEntrance' and vehicle not in rerouted_vehs: #Reroute to find a parking spot.
			parking_spot = find_parking_spot()
			if parking_spot is None:
				continue
			reroute_to_parking_spot(vehicle, parking_spot)
			vehicle_handler.highlight(vehicle)
			rerouted_vehs.append(vehicle)
			continue
		if current_edge in parkings_occ.keys():
			if parkings_occ[current_edge] is None:
				continue # There is a vehicle but is already leaving the parking
			parked_veh, end_time = parkings_occ[current_edge]
			if parked_veh == vehicle:
				if step > end_time:
					exit_parking(parked_veh, current_edge)
	pass


def store_parking_lots():
	global parkings_occ
	edgeHandler = traci.edge
	parkings = [edge for edge in edgeHandler.getIDList() if "pe" in edge and "pex" not in edge]
	parkings_occ = {key:None for key in parkings}


def simulate():
	global vehicle_handler, step, rerouted_vehs
	traci.start( sumoCmd )
	vehicle_handler = traci.vehicle
	store_parking_lots(  )
	step = 0
	rerouted_vehs = []
	while step < 1000:
		traci.simulationStep()
		#Your code
		apply_parking_logic()
		step += 1
	traci.close()


simulate()