import os, sys

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append( tools )
    networks = os.path.abspath( os.path.join( os.path.dirname( __file__ ), '..', 'networks' ) )
else:
    sys.exit("declare enviroment variable sumo_home")