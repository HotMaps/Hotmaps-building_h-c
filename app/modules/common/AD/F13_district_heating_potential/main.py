# -*- coding: utf-8 -*-
"""
Created on July 11 2017

@author: fallahnejad@eeg.tuwien.ac.at
"""
import os
import sys
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)
from AD.heat_density_map.main import HDMAP


def ad_f13():
    # path to the AD
    path = os.path.dirname(os.path.dirname(__file__))
    data_warehouse = path + os.sep + 'data_warehouse'
    heat_density_map = HDMAP(data_warehouse)
    region = data_warehouse + os.sep + 'AT.shp'
    # in GWh/km2
    pix_threshold = 10
    # in GWh/a
    DH_threshold = 30
    return (heat_density_map, region, pix_threshold, DH_threshold)


if __name__ == "__main__":
    output = ad_f13()
    for item in output:
        print(item)
