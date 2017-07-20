import geopandas as gpd
from geopandas.tools import overlay
import os
'''
this code overlays two polygon layers. The possible methods can be seen in dictionary "how_method" within the code.
'''

def overlaying(lyr1_path,lyr2_path,method,outLyr_path):
    how_method = {1: "intersection", 2: "union", 3: "symetrical difference", 4: "difference"}
    lyr1 = gpd.read_file(lyr1_path)
    lyr2 = gpd.read_file(lyr2_path)
    new_lyr = overlay(lyr1, lyr2, how=how_method[method])
    new_lyr.to_file(outLyr_path)

if __name__ == "__main__":
    prj_path = "/home/simulant/ag_lukas/personen/Mostafa/Lab"
    lyr1_path = prj_path + os.sep + "Pop_Nuts_Differ.shp"
    lyr2_path = prj_path + os.sep + "Pop_Nuts_merged.shp"
    method=2
    outLyr_path = prj_path + os.sep + "Pop_Nuts_Complete.shp"
    overlaying(lyr1_path, lyr2_path, method, outLyr_path)