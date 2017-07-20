# -*- coding: utf-8 -*-
"""
Created on July 11 2017

@author: fallahnejad@eeg.tuwien.ac.at
"""
import os
from AD.heat_density_map.main import HDMAP


def ad_f13():
    os.chdir('../..')
    data_warehouse = os.getcwd() + os.sep + 'AD/data_warehouse'
    heat_density_map = HDMAP(data_warehouse)
    region = data_warehouse + os.sep + 'AT.shp'
    # in GWh/km2
    pix_threshold = 10
    # in GWh/a
    DH_threshold = 30
    return (heat_density_map, region, pix_threshold, DH_threshold)


if __name__ == "__main__":
    ad_f13()
