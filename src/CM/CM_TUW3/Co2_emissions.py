'''
This script has been created in the context of the Hotmaps EU project.

@author: Sara Fritz
@Institute: TUW, Austria
@Contact: fritz@eeg.tuwien.ac.at
'''

#The CO2 emissions according for the buildings heat supply are calculated. 
def co2_emissions(energy_demand, efficiency, spec_co2_emissions):
    
    fed = (energy_demand / efficiency).rename('final_energy_demand')
    total_emissions=(spec_co2_emissions.multiply(fed,axis=0))
    specific_emissions=(total_emissions / energy_demand)
    
    return (specific_emissions, total_emissions)

