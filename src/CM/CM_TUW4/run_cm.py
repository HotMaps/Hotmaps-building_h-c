'''
Created on Jul 26, 2017

@author: simulant
'''
import os
import time
import sys
path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if path not in sys.path:
    sys.path.append(path)
import CM.CM_TUW4.district_heating_potential as DHP
from AD.heat_density_map.main import HDMAP


def main(heat_density_map, region, pix_threshold, DH_threshold):
    DH_Regions, arr1, rasterOrigin = DHP.DHReg(heat_density_map, region,
                                               pix_threshold, DH_threshold)
    return DH_Regions, arr1, rasterOrigin

if __name__ == "__main__":
    start = time.time()
    data_warehouse = path + os.sep + 'AD/data_warehouse'
    heat_density_map = HDMAP(data_warehouse)
    region = data_warehouse + os.sep + 'AT.shp'
    output_dir = path + os.sep + 'Outputs'
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    outRasterPath = output_dir + os.sep + 'Pot_AT_TH30.tif'
    # pix_threshold [GWh/km2]
    pix_threshold = 10
    # DH_threshold [GWh/a]
    DH_threshold = 30
    output = main(heat_density_map, region, pix_threshold, DH_threshold)
    elapsed = time.time() - start
    print("%0.3f seconds" % elapsed)
