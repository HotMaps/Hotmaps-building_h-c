# -*- coding: utf-8 -*-
"""
Created on July 24 2017

@author: fallahnejad@eeg.tuwien.ac.at
"""
import os
import sys
import time
import numpy as np
path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if path not in sys.path:
    sys.path.append(path)
'''
This module gets a demand value and uses the default distribution of heat
density map for distributing this value between pixels. The module returns a
numpy array.
'''


def scaling(hdm_cut, updated_demand):
    '''
    HDM_cut:        a cut of DHM for the selected region. The unit of heat
                    density is GWh/km2.
    desired demand: the value in GWh which will be distributed as of default
                    district heating map.
    updated_demand: new demand value in GWh.
    '''
    # GWh/km2 to GWh/ha; and sum over pixel values
    sum_demand_cut = np.sum(hdm_cut) * 0.01
    new_HDM_cut = updated_demand / sum_demand_cut * hdm_cut
    return new_HDM_cut


if __name__ == "__main__":
    start = time.time()
    hdm_cut = np.ones((50, 40))
    updated_demand = 10
    new_distribution = scaling(hdm_cut, updated_demand)
    print(new_distribution)
    elapsed = time.time() - start
    print("%0.3f seconds" % elapsed)
