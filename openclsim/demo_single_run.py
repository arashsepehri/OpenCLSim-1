import datetime, time
import simpy

import shapely.geometry
from simplekml import Kml, Style

# package(s) for data handling
import pandas as pd
import numpy as np

import openclsim.core as core
import openclsim.model as model
import openclsim.plot as plot

simulation_start = 0

my_env = simpy.Environment(initial_time=simulation_start)

# The generic site class
Site = type(
    "Site",
    (
        core.Identifiable,  # Give it a name
        core.Log,  # Allow logging of all discrete events
        core.Locatable,  # Add coordinates to extract distance information and visualize
        core.HasContainer,  # Add information on the material available at the site
        core.HasResource,
    ),  # Add information on serving equipment
    {},
)  # The dictionary is empty because the site type is generic

# Information on the extraction site - the "from site" - the "win locatie"
location_from_site = shapely.geometry.Point(4.18055556, 52.18664444)  # lon, lat

data_from_site = {
    "env": my_env,  # The simpy environment defined in the first cel
    "name": "Winlocatie",  # The name of the site
    "ID": "6dbbbdf4-4589-11e9-a501-b469212bff5d",  # For logging purposes
    "geometry": location_from_site,  # The coordinates of the project site
    "capacity": 10,  # The capacity of the site
    "level": 6,
}  # The actual volume of the site

# Information on the dumping site - the "to site" - the "dump locatie"
location_to_site = shapely.geometry.Point(4.25222222, 52.11428333)  # lon, lat

data_to_site = {
    "env": my_env,  # The simpy environment defined in the first cel
    "name": "Dumplocatie",  # The name of the site
    "ID": "6dbbbdf5-4589-11e9-82b2-b469212bff5c",  # For logging purposes
    "geometry": location_to_site,  # The coordinates of the project site
    "capacity": 6,  # The capacity of the site
    "level": 0,
}  # The actual volume of the site (empty of course)

# The two objects used for the simulation
from_site = Site(**data_from_site)
to_site = Site(**data_to_site)


# The generic class for an object that can move and transport (a TSHD for example)
TransportProcessingResource = type(
    "TransportProcessingResource",
    (
        core.Identifiable,  # Give it a name
        core.Log,  # Allow logging of all discrete events
        core.ContainerDependentMovable,  # A moving container, so capacity and location
        core.Processor,  # Allow for loading and unloading
        core.HasResource,  # Add information on serving equipment
        core.HasCosts,  # Add information on costs
        core.LoadingFunction,  # Add a loading function
        core.UnloadingFunction,  # Add an unloading function
    ),
    {},
)

# For more realistic simulation you might want to have speed dependent on the volume carried by the vessel
def compute_v_provider(v_empty, v_full):
    return lambda x: 10


# TSHD variables
data_hopper = {
    "env": my_env,  # The simpy environment
    "name": "Hopper 01",  # Name
    "ID": "6dbbbdf6-4589-11e9-95a2-b469212bff5b",  # For logging purposes
    "geometry": location_from_site,  # It starts at the "from site"
    "loading_rate": 1,  # Loading rate
    "unloading_rate": 1,  # Unloading rate
    "capacity": 4,  # Capacity of the hopper - "Beunvolume"
    "compute_v": compute_v_provider(5, 4.5),  # Variable speed
    "weekrate": 7,
}


hopper = TransportProcessingResource(**data_hopper)
#%%

# activity = model.GenericActivity(
#     env=my_env,  # The simpy environment defined in the first cel
#     name="Soil movement",  # We are moving soil
#     ID="6dbbbdf7-4589-11e9-bf3b-b469212bff5b",  # For logging purposes
#     )
single_run = []
shift_amount_activity_loading_data = { "env":my_env,  # The simpy environment defined in the first cel
    "name":"Transfer MP",  # We are moving soil
    "ID":"6dbbbdf7-4589-11e9-bf3b-b469212bff52",  # For logging purposes
    "processor":hopper,
    "origin":from_site,
    "destination":hopper,
    "amount":4,
    "postpone_start":True,
    }
single_run.append(model.ShiftAmountActivity(**shift_amount_activity_loading_data ))

move_activity_to_site_data = { "env":my_env,  # The simpy environment defined in the first cel
    "name":"sailing filler",  # We are moving soil
    "ID":"6dbbbdf7-4589-11e9-bf3b-b469212bff5b",  # For logging purposes
    "mover":hopper, 
    "destination":to_site,
    "postpone_start":True,}
single_run.append(model.MoveActivity(**move_activity_to_site_data ))

shift_amount_activity_unloading_data = { "env":my_env,  # The simpy environment defined in the first cel
    "name":"Transfer TP",  # We are moving soil
    "ID":"6dbbbdf7-4589-11e9-bf3b-b469212bff54",  # For logging purposes
    "processor":hopper,
    "origin":hopper,
    "destination":to_site,
    "amount":4,
    "postpone_start":True,
    }
single_run.append(model.ShiftAmountActivity(**shift_amount_activity_unloading_data ))

move_activity_to_harbor_data = { "env":my_env,  # The simpy environment defined in the first cel
    "name":"sailing empty",  # We are moving soil
    "ID":"6dbbbdf7-4589-11e9-bf3b-b469212bff5d",  # For logging purposes
    "mover":hopper, 
    "destination":from_site,
    "postpone_start":True,}
single_run.append(model.MoveActivity(**move_activity_to_harbor_data ))

sequential_activity_data = {"env"  : my_env,
                      "name" : "Single run process",
                      "ID":"6dbbbdf7-4589-11e9-bf3b-b469212bff60",  # For logging purposes
                      "sub_processes" : single_run,
                      "postpone_start":True}
activity = model.SequentialActivity(**sequential_activity_data)

while_data =  { "env":my_env,  # The simpy environment defined in the first cel
    "name":"while",  # We are moving soil
    "ID":"6dbbbdf7-4589-11e9-bf3b-b469212bff5g",  # For logging purposes
    "sub_processes": [activity],
    #"condition_event": [from_site.container.get_empty_event, to_site.container.get_full_event],
    "condition_event": to_site.container.full_event,
    "postpone_start": False}
while_activity = model.WhileActivity(**while_data) 

my_env.run()

log_df = pd.DataFrame(hopper.log)
data =log_df[['Message', 'ActivityState', 'Timestamp', 'Value', 'ActivityID']]
data = data.drop_duplicates()

while_df = pd.DataFrame(while_activity.log)
data_while = while_df[['Message', 'ActivityState', 'Timestamp', 'Value', 'ActivityID']]
data_while = data_while.drop_duplicates()

basic = []
for proc in single_run:
    df = pd.DataFrame(proc.log)
    basic.append(df[['Message', 'ActivityState', 'Timestamp', 'Value', 'ActivityID']])


#%%
print(f"hopper :{hopper.container.get_level()}")
print(f"from_site :{from_site.container.get_level()}")
print(f"to_site :{to_site.container.get_level()}")
c = to_site.container