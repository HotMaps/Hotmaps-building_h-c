import os
import time
import sys
import numpy as np
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)
import CM.CM_TUW3.Co2_emissions as CO2emissions


def main(energy_demand, efficiency_heatingsystem, spec_co2_emissions):
    values = CO2emissions.co2_emissions(energy_demand, efficiency_heatingsystem, spec_co2_emissions)
    return values

if __name__ == "__main__":
    print('calculation started')
    

