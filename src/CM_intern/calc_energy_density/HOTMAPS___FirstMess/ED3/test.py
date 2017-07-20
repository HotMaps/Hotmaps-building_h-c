import gdal
import os,time
from zonal_statistics import ZonalStat
from higherRes import HighRes




start_time = time.time()
elapsed_time = time.time()
if linux:
    prj_path    = "/home/simulant/ag_lukas/personen/Mostafa/HeatDensityMap - Copy"
else:
    prj_path    = "Z:/personen/Mostafa/HeatDensityMap - Copy"

org_data_path    = prj_path  + os.sep + "Original Data"
proc_data_path    = prj_path  + os.sep + "Processed Data"    
temp_path        = prj_path  + os.sep + "Temp"


input_zone_polygon = org_data_path + os.sep + "Geostat_pop.shp"
input_value_raster = proc_data_path + os.sep + "ss_pop_cut.tif"
jsonOutput = temp_path + os.sep + "ZS_clc.geojson"
output_path = temp_path + os.sep + "ZS_CLC.tif"
pixelWidth = 100
pixelHeight = 100
dataType = 'uint16'


landFactor = {1:1,2:1,3:1,4:0.05,10:0.3,11:0.3,12:0.3,20:0.5,21:0.3,41:0.05}

ds1 = gdal.Open(input_value_raster)
b11 = ds1.GetRasterBand(1)
arr1 = b11.ReadAsArray()
xRes = arr1.shape[0]
yRes = arr1.shape[1]

arr_out = np.zeros((x_res, y_res),dtype = dataType)

for i in range(xRes):
    for j in range(yRes):
        arr_out[i,j] = landFactor.setDefault{arr1[i,j],0.1}





ZonalStat(input_zone_polygon,input_value_raster, jsonOutput, output_path, ['sum'])
HighRes(output_path, pixelWidth, pixelHeight, dataType, r3, noDataValue)
elapsed_time = time.time() - elapsed_time
print("Process took: %s seconds" %elapsed_time)







landFactor.setDefault{key,0.1}