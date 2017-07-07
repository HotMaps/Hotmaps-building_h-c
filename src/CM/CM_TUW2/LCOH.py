# -*- coding: iso-8859-15 -*-
'''
This script has been created in the context of the Hotmaps EU project.

@author: Sara Fritz
@Institute: TUW, Austria
@Contact: fritz@eeg.tuwien.ac.at
'''

#This function calculates the levelized costs of heat (LCOH) in /MWh for one building 
def levelized_costs_of_heat(energy_demand, heat_load,energy_price,co2_costs, taxes, investment_costs, operation_and_maintenance_costs, efficiency_heatingsystem,r, lt, population):
    annuity = float( ( r * (1+r)**lt ) / ( (1+r)**lt - 1 ) ) 
    
    fed = (energy_demand/efficiency_heatingsystem).rename('final_energy_demand')
    var_costs = (operation_and_maintenance_costs*heat_load).rename('var_costs')
    fix_costs = (heat_load*investment_costs*annuity).rename('fix_costs')
    energy_costs = (fed*energy_price).rename('energy_costs')
    taxes = (taxes * fed).rename('taxes')
    co2_costs = (co2_costs * fed).rename('co2_costs')
    total_costs = (var_costs+fix_costs+energy_costs +taxes + co2_costs).rename('total_costs')  
    share_of_taxes = (taxes*fed / total_costs).rename('share_of_taxes')  
    lcoh = ((heat_load*investment_costs*annuity+fed*energy_price+operation_and_maintenance_costs*heat_load+co2_costs)/energy_demand).rename('LCOH')
    lcohcapita = ((heat_load*investment_costs*annuity+fed*energy_price+operation_and_maintenance_costs*heat_load+co2_costs)/population).rename('LCOH capita')
    
    return (var_costs, fix_costs,energy_costs, total_costs, share_of_taxes, co2_costs, lcoh, lcohcapita, fed)
    