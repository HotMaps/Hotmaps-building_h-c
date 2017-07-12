'''
This script has been created in the context of the Hotmaps EU project.

@author: Sara Fritz
@Institute: TUW, Austria
@Contact: fritz@eeg.tuwien.ac.at
'''

#The CO2 emissions according for the buildings heat supply are calculated. 
def co2_emissions(energy_demand, efficiency, spec_co2_emissions):
    
    fed = (energy_demand / efficiency).rename('final energy demand')
    total_emissions=(fed*spec_co2_emissions).rename('total CO2 emissions')
    specific_emissions=(total_emissions / energy_demand).rename('specific CO2 emissions')
    
    return (specific_emissions, total_emissions)

