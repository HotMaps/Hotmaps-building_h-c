import os
import json
import geopandas as gpd
from rasterstats import zonal_stats

'''
the statistics can be the following items:
min         max         mean        count
sum         std         median      majority
minority    unique      range       nodata

default statistic is "sum"
'''


def ZonalStat(input_zone_polygon,input_value_raster, jsonOutput, output_path,statistics=['sum']):
    statis = zonal_stats(input_zone_polygon,input_value_raster,nodata=0,stats=statistics, geojson_out=True)
    # statis = zonal_stats(input_zone_polygon,input_value_raster,stats=statistics, geojson_out=True)
    # print(statis)
    # print('\n')
    # print(statis[0].keys())
    result = {"type": "FeatureCollection", "features": statis}
    with open(jsonOutput, 'w') as outfile:
        json.dump(result, outfile)
    gdf = gpd.read_file(jsonOutput)
    gdf.to_file(output_path)
    
    # gdf = gpd.read_file(statis)
    # gdf.to_file(output_path)
    
if __name__ == "__main__":
    
    
    prj_path = "/home/simulant/ag_lukas/personen/Mostafa/EnergyDensityII"
    temp_path            = prj_path  + os.sep + "Temp"
    data_path            = prj_path  + os.sep + "Data"

    input_zone_polygon = prj_path + os.sep + "NUTS_Demand.shp"
    input_value_raster = data_path + os.sep + "Population.tif"
    jsonOutput= prj_path + os.sep + "test.geojson"
    output_path= prj_path + os.sep + "test.tif"
    statistics=['sum']
    ZonalStat(input_zone_polygon,input_value_raster,jsonOutput, output_path, statistics)