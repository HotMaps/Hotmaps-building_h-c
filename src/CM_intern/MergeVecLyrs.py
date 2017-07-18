import geopandas as gpd
import pandas as pd
import os
'''
This code can be used for two point layers with similar field names and field types in order to join them and make a union of both of them.

'''

def MergeLyrs(lyr1_path,lyr2_path,outLyr_path):
    lyr1 = gpd.read_file(lyr1_path)
    lyr2 = gpd.read_file(lyr2_path)
    dataframesList = [lyr1 , lyr2]
    outLyr = gpd.GeoDataFrame( pd.concat( dataframesList, ignore_index=True))
    outLyr.crs = {'init' : 'epsg:3035'}
    outLyr.to_file(outLyr_path)

if __name__ == "__main__":
    prj_path = "/home/simulant/ag_lukas/personen/Mostafa/Lab"
    lyr1_path = prj_path + os.sep + "Pop_Nuts_Differ.shp"
    lyr2_path = prj_path + os.sep + "Pop_Nuts_merged.shp"
    outLyr_path = prj_path + os.sep + "Pop_Nuts_Complete.shp"
    MergeLyrs(lyr1_path, lyr2_path, outLyr_path)