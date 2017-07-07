# -*- coding: utf-8 -*-
"""
Created on July 6 2017

@author: fallahnejad@eeg.tuwien.ac.at
"""
import os
import time
import ogr
import osr
import pandas as pd
'''
This module creates a shapefile with attributes which exist in the input
shapefile of shp2csv.py module and assigns the calculated values to the
features of this shapefile.
'''


def update_building_lyr(inputCSV, inShapefile, outShapefile):
    # fields in CSV are as follows:
    # ['hotmaps_ID', 'inputLyr_ID', 'Type', 'Year_Construction', 'Address',
    # 'Footprint', 'NrFloor', 'GFA', 'spec_demand', 'demand', 'X_3035',
    # 'Y_3035']
    ifile = pd.read_csv(inputCSV)
    ifile = ifile.sort_values(["hotmaps_ID"])
    csv_cols = ifile.columns.values
    col_dtype = ifile.dtypes.values
    # Get the input layer
    driver = ogr.GetDriverByName('ESRI Shapefile')

    inDataSource = driver.Open(inShapefile)
    inLayer = inDataSource.GetLayer()
    # set CRS
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(3035)
    outDriver = ogr.GetDriverByName("ESRI Shapefile")
    if os.path.exists(outShapefile):
        outDriver.DeleteDataSource(outShapefile)
    # Create the output shapefile
    outDataSource = outDriver.CreateDataSource(outShapefile)
    outLayer = outDataSource.CreateLayer("Building_lyr_updated", srs,
                                         geom_type=ogr.wkbPolygon)
    for i, item in enumerate(csv_cols):
        if i > 0:
            if col_dtype[i] == object:
                Field = ogr.FieldDefn(item, ogr.OFTString)
            elif col_dtype[i] == int:
                Field = ogr.FieldDefn(item, ogr.OFTInteger)
            else:
                Field = ogr.FieldDefn(item, ogr.OFTReal)
            outLayer.CreateField(Field)
    outLayerDefn = outLayer.GetLayerDefn()
    # loop through the input features
    inFeature = inLayer.GetNextFeature()
    while inFeature:
        fid = inFeature.GetFID()
        outFeature = ogr.Feature(outLayerDefn)
        # get the input geometry
        for i, item in enumerate(csv_cols):
            if i > 0:
                outFeature.SetField(outLayerDefn.GetFieldDefn(i-1).GetNameRef(),
                                    (ifile[item].values)[fid])
        geom = inFeature.GetGeometryRef()
        outFeature.SetGeometry(geom)
        outLayer.CreateFeature(outFeature)
        outFeature = None
        inFeature = inLayer.GetNextFeature()
        # Save and close DataSources
    inDataSource = None
    outDataSource = None

if __name__ == "__main__":
    start = time.time()
    inputCSV = "/home/simulant/ag_lukas/personen/Mostafa/Task 3.1/" \
               "NoDemandData/Bistrita.csv"
    outShapefile = "/home/simulant/ag_lukas/personen/Mostafa/Task 3.1/" \
                   "NoDemandData/Bistrita_new.shp"
    inShapefile = "/home/simulant/ag_lukas/personen/Mostafa/Task 3.1/" \
                  "NoDemandData/Bistrita_3035.shp"
    update_building_lyr(inputCSV, inShapefile, outShapefile)
    print(time.time() - start)
