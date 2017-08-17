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

import AD.F14_input.main as data

import CM.CM_TUW2.run_cm as CM2
import CM.CM_TUW3.run_cm as CM3

import pandas
import numpy
import json

def execute(interest_rate, lifetime, user_input_nuts0, user_input_nuts3, population, energy_demand, heat_load):
    
    
    (co2_costs, energy_price, taxes, investment_costs, operation_and_maintenance_costs, efficiency_heatingsystem, spec_co2_emissions, heating_system_names)\
        =data.ad_f14(user_input_nuts3, user_input_nuts0)
    
    (var_costs, fix_costs,energy_costs, total_costs, share_of_taxes, co2_costs, lcoh, lcohcapita, fed) = \
        CM2.main(energy_demand, heat_load,energy_price,co2_costs, taxes, investment_costs, operation_and_maintenance_costs, efficiency_heatingsystem,interest_rate,lifetime,population)
    (specific_emissions, total_emissions) = CM3.main(energy_demand, efficiency_heatingsystem, spec_co2_emissions)
    
    name_heating_systems = (pandas.Series(heating_system_names)).rename('Heating System')
    export_dataframe=pandas.concat([name_heating_systems,var_costs,fix_costs, energy_costs, total_costs, share_of_taxes, co2_costs, lcoh, lcohcapita, fed, specific_emissions, total_emissions],axis=1)
    
    #return [var_costs, fix_costs,energy_costs, total_costs, share_of_taxes, co2_costs, lcoh, lcohcapita, fed,specific_emissions, total_emissions]
    #return export_dataframe

    test = export_dataframe
    export_dataframe = export_dataframe.set_index('Heating System') 
    dictionary= json.loads( export_dataframe.to_json() )
    
    
    return dictionary


if __name__ == "__main__":
    print('calculation started')
    output_dir = path + os.sep + 'Outputs'
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    interest_rate = 1.06
    lifetime = 20
    
    ##Information from selected area
    user_input_nuts0 = 'AT'
    user_input_nuts3 = 'AT130'
    population = 1800000 #not final - just value
    
    #user input
    sel_building_energy_demand= 120 # kWh/a
    sel_building_heat_load = 20 #kW/a

    result = execute(interest_rate, lifetime,user_input_nuts0, user_input_nuts3, population, sel_building_energy_demand, sel_building_heat_load)
    print(result)
    print('calculation done')
    
    



    