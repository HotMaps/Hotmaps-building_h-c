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

def execute():

    #scalars      
    energy_demand=data.sel_building_energy_demand
    heat_load=data.sel_building_heat_load
    co2_costs=data.NUTS3_co2_costs['2015'].values
    r=data.interest_rate
    population = data.population
    #list of floats
    lt=data.lifetime
    energy_price= data.NUTS0_household_energy_prices['2015']
    taxes=data.taxes_per_heating_system['2015']
    investment_costs=data.investment_costs_heating_system['Investmentcosts']
    operation_and_maintenance_costs=data.OandM_costs_heating_system['O&m']
    efficiency_heatingsystem=data.efficiency_heating_system['efficiency']
    spec_co2_emissions=pandas.DataFrame(numpy.transpose(data.specific_co2_emissions[data.specific_co2_emissions.columns[data.investment_costs_heating_system.idx_heatingsystem.values]].values)).T.squeeze()##T.squeeze generates an pandas series
                
    (var_costs, fix_costs,energy_costs, total_costs, share_of_taxes, co2_costs, lcoh, lcohcapita, fed) = CM2.main(energy_demand, heat_load,energy_price,co2_costs, taxes, investment_costs, operation_and_maintenance_costs, efficiency_heatingsystem,r, lt,population)
    (specific_emissions, total_emissions) = CM3.main(energy_demand, efficiency_heatingsystem, spec_co2_emissions)
    
    name_heating_systems = (pandas.Series(data.investment_costs_heating_system['heating system'].values)).rename('Heating System')
    export_dataframe=pandas.concat([name_heating_systems,var_costs,fix_costs, energy_costs, total_costs, share_of_taxes, co2_costs, lcoh, lcohcapita, fed, specific_emissions, total_emissions],axis=1)
    
    #return [var_costs, fix_costs,energy_costs, total_costs, share_of_taxes, co2_costs, lcoh, lcohcapita, fed,specific_emissions, total_emissions]
    return export_dataframe

if __name__ == "__main__":
    print('calculation started')
    output_dir = path + os.sep + 'Outputs'
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    result = execute()
    print(result)
    print('calculation done')
    
    



    