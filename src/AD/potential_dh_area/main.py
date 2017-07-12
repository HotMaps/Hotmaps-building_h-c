# -*- coding: utf-8 -*-
"""
Created on July 11 2017

@author: fallahnejad@eeg.tuwien.ac.at
"""
import os


def default_hdm():
    data_warehouse = os.path.dirname(os.path.dirname(os.getcwd())) + \
                     '/AD/data_warehouse/'
    heat_density_map = data_warehouse + 'top_down_heat_density_map_v2.tif'
    strd_vector = data_warehouse + 'EU28_plus_CH.shp'
    # in GWh/km2
    pix_threshold = 10
    # in GWh/a
    DH_threshold = 30
    return (heat_density_map, strd_vector, pix_threshold, DH_threshold)


if __name__ == "__main__":
    default_hdm()
