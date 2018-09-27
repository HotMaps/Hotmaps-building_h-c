'''
Created on Apr 20, 2017

@author: simulant
'''
import os


def HDMAP(data_warehouse):
    path_2_hdm = data_warehouse + '/heat_tot_curr_density_AT.tif'
    return path_2_hdm


if __name__ == "__main__":
    # path to the src
    data_warehouse = os.path.dirname(os.path.
                                     dirname(os.path.abspath(__file__))) + \
                                                    os.sep + 'data_warehouse'
    path2hdm = HDMAP(data_warehouse)
    print(path2hdm)
