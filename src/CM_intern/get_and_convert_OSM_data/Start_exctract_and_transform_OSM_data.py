'''
Created on Jul 24, 2017

@author: Andreas

run this script to calculate the energy density maps
'''


import sys
from extract_transform_OSM import ExtractAndTransformOSMData




if __name__ == "__main__":
    
    print(sys.version_info)
    input_data_path = "/home/simulant/ag_lukas/personen/Andreas/Openstreetmapdata"
    output_data_path = "/home/simulant/workspace/project/hotmaps/HOTMAPS___FirstMess/openstreetmap/extract"
    
    # Prepare
    EZOSM = ExtractAndTransformOSMData(input_data_path, output_data_path)
    
    EZOSM.extract_and_reproject_files()
   
    print("Done!")

