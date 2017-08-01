'''
Created on Jul 26, 2017

@author: simulant
'''
import os
import time
import sys
import numpy as np
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)
import CM.CM_TUW18.scaling_hdm as scale


def main(hdm_cut, updated_demand):
    new_distribution = scale.scaling(hdm_cut, updated_demand)
    return new_distribution

if __name__ == "__main__":
    start = time.time()
    hdm_cut = np.ones((50, 40))
    updated_demand = 10
    new_distribution = main(hdm_cut, updated_demand)
    print(new_distribution)
    elapsed = time.time() - start
    print("%0.3f seconds" % elapsed)
