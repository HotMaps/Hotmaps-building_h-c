'''
Created on Apr 20, 2017

@author: simulant
'''
import numpy as np
import gdal
import pdb

def default_hdm():
    heat_density_map, strd_vector, pix_threshold, DH_threshold

 
def HDMAP(file):
    """
    returns heat density map

    Output:
    """
    
    #heat_density_map = np.reshape(np.random.rand((120)), (12, 10))
    heat_density_map = file
    heat_density_map = gdal.Open(heat_density_map)
    return heat_density_map




if __name__ == "__main__":
    
    HDMAP()