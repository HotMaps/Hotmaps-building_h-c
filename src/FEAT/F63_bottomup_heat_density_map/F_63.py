import AD.available_data as data
from CM.CM_TUW9.main_block import main
import os


def execute():
    '''
    process_bool: (process1, process2, process3, process4)
    process1: specific demand will be rasterized. If False, load from data
              warehouse 
    process2: input shapefile to standardized csv 
    process3: update the input shapefile
    process4: create the heat density map
    ###########################################################################
    inputValues = (eu_shp, spec_demand_csv, spec_demand_shp, 
                   UsefulDemandRasterPath, UsefulDemandRaster, inShapefile,
                   outCSV, outShapefile, heatDensityRaster, populaion)
    eu_shp: used for rasterize the specific demand in eu level.
    spec_demand_csv: specific heat demand for each country, each sector in
                     [kWh/m2] 
    spec_demand_shp: shapefile created based on eu_shp and spec_demand_csv
    UsefulDemandRasterPath: path/to/save/specificdemandrasters
    UsefulDemandRaster: ['path/ResidentialUsefulDemand.tif',
                         'path/ServiceUsefulDemand.tif'] 
    inShapefile: input shapefile by user
    outCSV: standard CSV
    outShapefile: updated shapefile based on uploaded shapefile by user
    heatDensityRaster: 
    population: population in selected area
    '''
    process_bool = data.bu_hdm_process()
    inputValues = data.bu_hdm_inputs()
    main(process_bool, inputValues)


if __name__ == "__main__":
    execute()
    