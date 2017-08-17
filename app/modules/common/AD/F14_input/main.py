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

import numpy
from . import import_data
import os
import pandas as pandas



def ad_f14(user_input_nuts3, user_input_nuts0):
    # path to the AD
    path = os.path.dirname(os.path.dirname(__file__))
    path_data = os.path.join(path,'data_warehouse')

    NUTS0_household_energy_prices = import_data.read_data_set_csv(os.path.join( path_data, 'AD.TUW.10_AT_household_energy_prices.csv')) #/kWh
    taxes_per_heating_system = import_data.read_data_set_csv(os.path.join( path_data, 'AD.TUW.4_AT_taxes_heating_systems.csv')) #€/kWh
    
    NUTS3_co2_costs = import_data.read_data_set_csv_NUTS3(os.path.join( path_data, 'AD.TUW.5_NUTS3_CO2costs.csv'),user_input_nuts3)  #/kWh
    specific_co2_emissions = import_data.read_data_set_csv_NUTS3(os.path.join( path_data, 'AD.ISI.5_NUTS3_specific_CO2emission.csv'), user_input_nuts3) #kg/kWh_emmitiert
    
    investment_costs_heating_system = import_data.read_data_set_csv(os.path.join( path_data, 'AD.TUW.7_EU28_costs_heating_systems.csv')) #/kW
    efficiency_heating_system = import_data.read_data_set_csv(os.path.join( path_data, 'AD.TUW.13_EU28_efficiency_heating_systems.csv')) #/kW
    OandM_costs_heating_system = import_data.read_data_set_csv(os.path.join( path_data, 'AD.TUW.7_EU28_costs_heating_systems.csv')) #/kW
    
    co2_costs=NUTS3_co2_costs['2015'].values
    energy_price= NUTS0_household_energy_prices['2015']
    taxes=taxes_per_heating_system['2015']
    investment_costs=investment_costs_heating_system['Investmentcosts']
    operation_and_maintenance_costs=OandM_costs_heating_system['O&m']
    efficiency_heatingsystem=efficiency_heating_system['efficiency']
    spec_co2_emissions=pandas.DataFrame(numpy.transpose(specific_co2_emissions[specific_co2_emissions.columns[investment_costs_heating_system.idx_heatingsystem.values]].values)).T.squeeze()##T.squeeze generates an pandas series
    heating_systems_names=investment_costs_heating_system['heating system'].values
    
    return (co2_costs, energy_price, taxes, investment_costs, operation_and_maintenance_costs, efficiency_heatingsystem, spec_co2_emissions, heating_systems_names)


if __name__ == "__main__":
    user_input_nuts0 = 'AT'
    user_input_nuts3 = 'AT130'
    output = ad_f14(user_input_nuts3, user_input_nuts0)


#interest_rate = 1.06
#lifetime = 20

##Information from selected area
#user_input_nuts0 = 'AT'
#user_input_nuts3 = 'AT130'
#population = 1800000 #not final - just value

#user input
#sel_building_energy_demand= 120 # kWh/a
#sel_building_heat_load = 20 #kW/a




