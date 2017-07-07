'''
Created on Apr 20, 2017

@author: simulant
'''
import numpy as np
from skimage import morphology, measure
from skimage.morphology import binary_closing, binary_dilation, binary_erosion, square


import AD.available_data  as AD_ 
 
def potDHAreas(heat_density_map,pix_threshold,DH_threshold, minSizeObj=3,minSizeHole=5, bridge = square(2), conn=2):
    """
    Calculate potential district heating areas
    input:
        heat_density_map: numpy array created from heat density map containing demand in 1ha pixels
        threshold: minimum demand in each pixel which makes it potential part of DH area
        minSizeObj: minimum area to be covered by connected object justifying development of district heating.
        minSizeHole: removes the holes smaller than this size
        bridge: square(2): The neighborhood expressed as a 2-D array of 1's and 0's. In our problem, "square(2)" refers to 100m distance.  
        conn: The connectivity defining the neighborhood of a pixel. it should be set to "2" to consider diagonal connectivities (DO NOT CHANGE IT UNLESS for a good reason).
        
    Output:
        DH: a boolean 2-D array with elements of "1" for potential district heating areas with the same resolution of the input "heat_density_map"
    
    
    """
    
    g = heat_density_map*(heat_density_map>pix_threshold)
    DH = (heat_density_map>pix_threshold).astype(bool)
    
#     temp1 = binary_dilation(DH, square(3)).astype(bool)
#     temp  = binary_erosion(temp1, square(1)).astype(bool)
    
    
    
    temp=DH.astype(bool)
    
    # "closing" process joins neighboring islands with a distant of no more than 100m for default "bridge" value.
#     temp = binary_closing(DH, square(3)).astype(bool)
    
    
    
    # removes connected objects that are smaller than "minSizeObj". also the connected Null objects within non-zero connected object are removed if they have a size of "smaller" than "minSizeHole"
    blobs1 = morphology.remove_small_objects(temp, min_size=minSizeObj, connectivity=conn)
    blobs  = morphology.remove_small_holes(blobs1, min_size=minSizeHole).astype(int)
    #blobs = blobs1.astype(int)
    
#    all_labels = measure.label(blobs)
#################################################################################################################################################################################
#   important note: the value of "1" is added to blobs_labels becouse in the existing version of python in server 155 the background values are returned as "-1". However, in Anaconda, the background elements are 0.
#                   in case this changed, consider relevant change in "for" loop in the foloowings. 
#################################################################################################################################################################################
    blobs_labels = measure.label(blobs, background=0)
    blobs_labels +=1
    numLabels = np.amax(blobs_labels)
    
    for i in range(numLabels+1):
        m = g * (blobs_labels==i)
        if np.sum(m) < DH_threshold:
            g[blobs_labels==i] = 0
            blobs_labels[blobs_labels==i] = 0
    DH=blobs_labels.astype(bool).astype(int)
    #DH=DH.astype(int)
    
    

    print(DH)
    print np.sum(DH)
    
    return









if __name__ == "__main__":
    

    potDHAreas(AD_.heat_density_map,0.1,10, 4,5)
    