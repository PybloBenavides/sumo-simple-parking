import os,sys
import sumocfg
import traci

from sumolib import checkBinary

sumoBinary = checkBinary('sumo-gui')

sumoCmd = [sumoBinary, '-c', os.path.join(sumocfg.networks, r"simple_network\simple.sumocfg")]

parkings_occ = None

def check_parking_lots():
	global parkings_occ
	for parking, occupancy in parkings_occ.items():
		if occupancy is None:
			return parking
	return None

def apply_parking_logic(vehicleHandler):
	for vehicle in vehicleHandler.getIDList():
		currentEdge = vehicleHandler.getRoadID( vehicle )
		if currentEdge == 'pEntrance': #Reroute to find a parking spot.
			check_parking_lots()
	pass


def store_parking_lots(edgeHandler):
	global parkings_occ
	parkings = [edge for edge in edgeHandler.getIDList() if "pe" in edge and "pex" not in edge]
	parkings_occ = {key:None for key in parkings}

def simulate():
	traci.start( sumoCmd )
	vehicleHandler = traci.vehicle
	edgeHandler = traci.edge
	store_parking_lots( edgeHandler )
	step = 0
	while step < 1000:
		traci.simulationStep()
		#Your code
		apply_parking_logic(vehicleHandler)
		step += 1
	traci.close()


simulate()