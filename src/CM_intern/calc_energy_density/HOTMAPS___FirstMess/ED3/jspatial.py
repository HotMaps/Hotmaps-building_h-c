import geopandas as gpd
import os, time
from geopandas.tools import sjoin

# required time ~ 1289 seconds on local computer
# target layer could be potentially the point layers
# join layer could be potentially the polygon layer
def spatialjoin(targetLyrPath, joinLyrPath, method, outVectorPath):
    op_method = {1:"intersects", 2: "within", 3:"contains"}
    target_lyr = gpd.read_file(targetLyrPath)
    join_lyr = gpd.read_file(joinLyrPath)
    
    target_lyr.head()
    join_lyr.head()
    
    result = sjoin(target_lyr, join_lyr, how="inner", op=op_method[method])
    result.to_file(outVectorPath)

    
if __name__ == "__main__":
    start_time = time.time()
    
    prj_path = "/home/simulant/ag_lukas/personen/Mostafa/EnergyDensityII"
    prj2_path = "/home/simulant/ag_lukas/personen/Mostafa/Lab"
    temp_path            = prj_path  + os.sep + "Temp"
    data_path            = prj_path  + os.sep + "Data"
    
    targetLyrPath = prj2_path + os.sep + "Pop_Nuts_Complete.shp"
    joinLyrPath = data_path + os.sep + "GEOSTAST_Pop_3035.shp"
    outVectorPath =  prj2_path + os.sep + "Pop_Nuts.shp"
    method = 2
    
    spatialjoin(targetLyrPath, joinLyrPath, method, outVectorPath)
    elapsed_time = time.time() - start_time
    print(elapsed_time)    