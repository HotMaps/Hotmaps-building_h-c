'''
Created on Apr 20, 2017

@author: simulant
'''
import numpy as np

def default_hdm():
    heat_density_map, strd_vector, pix_threshold, DH_threshold

def calc_level(strd_vector):
    return shapefile of NUTS0,1,2,3

def bu_hdm_inputs():
    (eu_shp, spec_demand_csv, spec_demand_shp, 
                   UsefulDemandRasterPath, UsefulDemandRaster, inShapefile,
                   outCSV, outShapefile, heatDensityRaster, population)
    
def bu_hdm_process():
    '''
    process_bool: (process1, process2, process3, process4)
    process1: specific demand will be rasterized. If False, load from data
              warehouse 
    process2: input shapefile to standardized csv 
    process3: update the input shapefile
    process4: create the heat density map
    '''
    (process1, process2, process3, process4) = (False, True, True, True)
    process = (process1, process2, process3, process4)
    return process


if __name__ == "__main__":
    
    HDMAP()