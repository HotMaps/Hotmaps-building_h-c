import os
import time
import sys
import numpy as np
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)
import CM.CM_TUW18.scaling_hdm as scale
import CM.CM_TUW19.run_cm as CM19
import CM.CM_TUW22.run_cm as CM22
from CM.CM_TUW1.read_raster import raster_array as RA


def main(hdm_path, selected_area, updated_demand_value, output_dir,
         outRasterPath):
    hdm, gt = RA(hdm_path, return_gt=True)
    hdm_cut, geo_transform = CM22.main(hdm, selected_area, output_dir, gt,
                                       nodata=0, return_array=True)
    scale.scaling(hdm_cut, geo_transform, updated_demand_value, outRasterPath)
