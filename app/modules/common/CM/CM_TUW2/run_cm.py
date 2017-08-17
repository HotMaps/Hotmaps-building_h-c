import os
import time
import sys
import numpy as np
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)
import CM.CM_TUW2.LCOH as LCOH


def main(energy_demand, heat_load,energy_price,co2_costs, taxes, investment_costs, operation_and_maintenance_costs, efficiency_heatingsystem,r, lt,population):
    values = LCOH.levelized_costs_of_heat(energy_demand, heat_load,energy_price,co2_costs, taxes, investment_costs, operation_and_maintenance_costs, efficiency_heatingsystem,r, lt,population)
    return values

if __name__ == "__main__":
    print('calculation started')

