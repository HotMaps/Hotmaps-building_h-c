# -*- coding: utf-8 -*-
"""
Created on July 24 2017

@author: fallahnejad@eeg.tuwien.ac.at
"""
import os
import sys
import time
import numpy as np
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)
import CM.CM_TUW19.run_cm as CM19
from CM.CM_TUW0.rem_mk_dir import rm_mk_dir, rm_file


def scaling(hdm_cut, hdm_cut_gt, updated_demand, outRasterPath):
    '''
    This module gets a demand value and uses the default distribution of heat
    density map for distributing this value between pixels. The module returns
    a numpy array.
    hdm_cut:          numpy array showing demand in MWh/ha
    hdm_cut_gt:       raster geo-transform
    updated_demand:   in GWh/a
    outRasterPath:    path for saving the updated hdm
    '''
    # Sum over pixel values in MWh/ha and return in GWh
    sum_demand_cut = np.sum(hdm_cut) * 0.001
    new_HDM_cut = updated_demand / sum_demand_cut * hdm_cut
    rm_file(outRasterPath)
    CM19.main(outRasterPath, hdm_cut_gt, "float32", new_HDM_cut)
    return outRasterPath


if __name__ == "__main__":
    start = time.time()
    hdm_cut = np.ones((50, 40))
    hdm_cut_gt = [4600500.0, 100.0, 0.0, 2828000.0, 0.0, -100.0]
    updated_demand = 10
    out_dir = path + os.sep + 'Outputs'
    rm_mk_dir(out_dir)
    outRasterPath = out_dir + os.sep + 'hdm_scaled.tif'
    new_distribution = scaling(hdm_cut, hdm_cut_gt, updated_demand,
                               outRasterPath)
    elapsed = time.time() - start
    print("%0.3f seconds" % elapsed)
