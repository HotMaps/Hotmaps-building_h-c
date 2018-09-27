"""
Created on July 24 2017

@author: fallahnejad@eeg.tuwien.ac.at
"""
import os
import sys
from osgeo import gdal
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)
from AD.heat_density_map.main import HDMAP


def ad_f107():
    # path to the AD
    path = os.path.dirname(os.path.dirname(__file__))
    data_warehouse = path + os.sep + 'data_warehouse'
    selected_area = data_warehouse + os.sep + 'AT312.shp'
    hdm_path = HDMAP(data_warehouse)
    return selected_area, hdm_path


if __name__ == "__main__":
    selected_area, hdm = ad_f107()
    print(selected_area)
    if isinstance(hdm, gdal.Dataset):
        print('Heat density map loaded successfully!')
