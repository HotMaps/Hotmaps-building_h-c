# -*- coding: utf-8 -*-
'''
This script has been created in the context of the Hotmaps EU project.

@author: Sara Fritz
@Institute: TUW, Austria
@Contact: fritz@eeg.tuwien.ac.at
'''
import os
import sys
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)

import numpy as np
from . import import_data
import os
import pandas as pandas

interest_rate = 1.06
lifetime = 20

##Information from selected area
user_input_nuts0 = 'AT'
user_input_nuts3 = 'AT130'
population = 1800000 #not final - just value

#user input
sel_building_energy_demand= 120 # kWh/a
sel_building_heat_load = 20 #kW/a


path_data = os.path.join(path,'AD/data_warehouse')

NUTS0_household_energy_prices = import_data.read_data_set_csv(os.path.join( path_data, 'AD.TUW.10_AT_household_energy_prices.csv')) #/kWh
taxes_per_heating_system = import_data.read_data_set_csv(os.path.join( path_data, 'AD.TUW.4_AT_taxes_heating_systems.csv')) #€/kWh

NUTS3_co2_costs = import_data.read_data_set_csv_NUTS3(os.path.join( path_data, 'AD.TUW.5_NUTS3_CO2costs.csv'),user_input_nuts3)  #/kWh
specific_co2_emissions = import_data.read_data_set_csv_NUTS3(os.path.join( path_data, 'AD.ISI.5_NUTS3_specific_CO2emission.csv'), user_input_nuts3) #kg/kWh_emmitiert

investment_costs_heating_system = import_data.read_data_set_csv(os.path.join( path_data, 'AD.TUW.7_EU28_costs_heating_systems.csv')) #/kW
efficiency_heating_system = import_data.read_data_set_csv(os.path.join( path_data, 'AD.TUW.13_EU28_efficiency_heating_systems.csv')) #/kW
OandM_costs_heating_system = import_data.read_data_set_csv(os.path.join( path_data, 'AD.TUW.7_EU28_costs_heating_systems.csv')) #/kW

