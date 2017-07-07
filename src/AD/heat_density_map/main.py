'''
Created on Apr 20, 2017

@author: simulant
'''
import numpy as np



 
def HDMAP():
    """
    returns heat density map
    
    
    Output:
    
    
    
    """
    
    heat_density_map = np.reshape(np.random.rand((120)), (12, 10))

    return heat_density_map







if __name__ == "__main__":
    
    HDMAP()