import os,sys
import sumocfg
import traci

from sumolib import checkBinary

sumoBinary = checkBinary('sumo-gui')

sumoCmd = [sumoBinary, '-c', os.path.join(sumocfg.networks, r"simple_network\simple.sumocfg")]

def apply_parking_logic(vehicleHandler):
	pass


def simulate():
	traci.start( sumoCmd )
	vehicleHandler = traci.vehicle
	step = 0
	while step < 1000:
		traci.simulationStep()
		#Your code
		apply_parking_logic(vehicleHandler)
		step += 1
	traci.close()


simulate()