'''
Created on Jul 24, 2017

@author: Andreas

run this script to calculate the energy density maps
'''

import sys
from calcDensity import ClassCalcDensity




if __name__ == "__main__":
    
    print(sys.version_info)
    pr_path = "./HOTMAPS___FirstMess/ED3/DATA"
    CD = ClassCalcDensity(pr_path)
    
    #Nuts3 Regions
    NUTS3_feat_id_LIST = [14]  # 14refers to the feature ID of Vienna
    NUTS3_feat_id_LIST = range(0,20000)  # 14refers to the feature ID of Vienna
    NUTS3_feat_id_LIST = range(12,15)

    CD.main_process(NUTS3_feat_id_LIST)
    
    print("Done!")

