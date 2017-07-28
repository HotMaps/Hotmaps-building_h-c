'''
Created on Jul 24, 2017

@author: Andreas

run this script to calculate the energy density maps
'''

import sys
sys.path.insert(0,"../..")
from CM_intern.calc_energy_density.calcDensity import ClassCalcDensity


def main(pr_path, NUTS3_feat_id_LIST):
    
    CD = ClassCalcDensity(pr_path)
    CD.main_process(NUTS3_feat_id_LIST)
    return

if __name__ == "__main__":
    
    print(sys.version_info)
    pr_path = "/home/simulant/workspace/project/Hotmaps_DATA/heat_density_map/"
    
    
    #Nuts3 Regions
    NUTS3_feat_id_LIST = [14]  # 14refers to the feature ID of Vienna
    NUTS3_feat_id_LIST = range(0,20000)  # 14refers to the feature ID of Vienna
    NUTS3_feat_id_LIST = range(12,15)
    NUTS3_feat_id_LIST = [14]
    main(pr_path, NUTS3_feat_id_LIST)
    
    print("Done!")

