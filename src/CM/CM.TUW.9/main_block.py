# -*- coding: utf-8 -*-
"""
Created on July 6 2017

@author: fallahnejad@eeg.tuwien.ac.at
"""
import time
from bottom_up_hdm import zonStat_selectedArea as zs
from specific_demand import specific_demand
from shp2csv import shp2csv
from update_building_layer import update_building_lyr as update
''' This module calls other calculation modules for the BUHDM'''


def main(process_bool, inputValues):
    (eu_shp, spec_demand_csv, spec_demand_shp, targetfield, UsefulDemandRaster,
     inShapefile, outCSV, outShapefile, heatDensityRaster) = inputValues
    # Process 1: creates a specific demand raster layer. The country names in
    # csv should be similar to the ones in the shapefile.
    if process_bool[0]:
        start = time.time()
        specific_demand(eu_shp, spec_demand_csv, spec_demand_shp, targetfield,
                        UsefulDemandRaster)
        print('Process 1 took: %0.2f seconds' % (time.time() - start))
    # Process 2: creates a standard csv file from the input shapefile
    if process_bool[1]:
        start = time.time()
        shp2csv(inShapefile, UsefulDemandRaster, outCSV)
        print('Process 2 took: %0.2f seconds' % (time.time() - start))
    # Process 3: updates and creates a new shapefile based on the standard csv
    if process_bool[2]:
        start = time.time()
        inputCSV = outCSV
        update(inputCSV, inShapefile, outShapefile)
        print('Process 3 took: %0.2f seconds' % (time.time() - start))
    # Process 4: generates a heat density map
    if process_bool[3]:
        inputCSV = outCSV
        start = time.time()
        zs(inputCSV, heatDensityRaster)
        print('Process 4 took: %0.2f seconds' % (time.time() - start))

if __name__ == "__main__":
    start = time.time()
    region = 'Bistrita'
    targetfield = 'Resid.'
    process1 = False
    process2 = True
    process3 = False
    process4 = True
    project_path = "/home/simulant/ag_lukas/personen/Mostafa/Task 3.1/" \
                   "NoDemandData/"
    eu_shp = project_path + "EU28.shp"
    spec_demand_csv = project_path + "useful demand.csv"
    spec_demand_shp = project_path + "EnergyUseEU28.shp"
    UsefulDemandRaster = project_path + "ResidentialUsefulDemand.tif"
    inShapefile = project_path + region + "_3035.shp"
    outCSV = project_path + region + ".csv"
    outShapefile = project_path + region + "_new.shp"
    heatDensityRaster = project_path + region + "_HDM.tif"
    process_bool = (process1, process2, process3, process4)
    inputValues = (eu_shp, spec_demand_csv, spec_demand_shp, targetfield,
                   UsefulDemandRaster, inShapefile, outCSV, outShapefile,
                   heatDensityRaster)
    main(process_bool, inputValues)
    print('The whole process took %0.2f seconds' % (time.time() - start))
