'''
Created on Apr 20, 2017

@author: simulant
'''
import AD.heat_density_map.main as DHM
import numpy as np
from potential_dh_area.main import default_hdm

heat_density_map = default_hdm()


heat_density_map = DHM.HDMAP("/home/simulant/workspace_mostafa/Hotmaps/Hotmaps/src/AD/data_warehouse/top_down_heat_density_map_v2.tif")
strd_vector_path = "/home/simulant/ag_lukas/personen/Mostafa/" \
                       "DHpot/Austria.shp"


