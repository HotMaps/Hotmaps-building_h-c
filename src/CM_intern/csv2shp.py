# -*- coding: utf-8 -*-
"""
Created on Thu May 4 2017

@author: Mostafa
"""
import ogr, osr
import pandas as pd
import numpy as np
import warnings, os
import time
#from asyncio.windows_events import NULL

'''
This is an old comment:
This code reads the CSV file containing demand values and creates a shapefile with a NUTS3 code field as well as all demand columns within the CSV file.
The first row of the CSV file should be the header. 
In oder to comply with other modules, make sure that the outShpPath is set with the right name and path: Original Data/NUTS_Demand.shp
'''

def Excel2shapefile(inShpPath, inCSV, outShpPath):
    
#     if outShpPath[-15:] != "NUTS_Demand.shp":
#          warnings.warn("The output name is not set to 'NUTS_Demand'. This can cause a problem when you run other modules to generate Heat Density Map!")
    
    # set CRS
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(3035)
    # Create the output Layer
    outShapefile = outShpPath
    outDriver = ogr.GetDriverByName("ESRI Shapefile")
    # Remove output shapefile if it already exists
    if os.path.exists(outShapefile):
        outDriver.DeleteDataSource(outShapefile)
    outDriver = ogr.GetDriverByName("ESRI Shapefile")
    # Create the output shapefile
    outDataSource = outDriver.CreateDataSource(outShapefile)
    outLayer = outDataSource.CreateLayer("NUTS_Demand", srs, geom_type=ogr.wkbPolygon)
    
    # read CSV file
    ifile = pd.read_csv(inCSV)
    df = ifile.values
    ID = ifile['id']
    check_null = pd.read_csv(inCSV).notnull().values
    # read the headers (first row of each column)
    fieldNames = pd.read_csv(inCSV, nrows=1).columns.values
    

    for i, item in enumerate(fieldNames):
        if i == 0:
            Field = ogr.FieldDefn(fieldNames[i], ogr.OFTString)
            outLayer.CreateField(Field)
#         elif i == 110:
#             Field = ogr.FieldDefn(fieldNames[i], ogr.OFTInteger64)
#             outLayer.CreateField(Field)
        else:
            Field = ogr.FieldDefn(fieldNames[i], ogr.OFTReal)
            outLayer.CreateField(Field)  
    # Get the output Layer's Feature Definition
    outLayerDefn = outLayer.GetLayerDefn()
    
    # read the input shapefile
    inShapefile = inShpPath
    inDriver = ogr.GetDriverByName("ESRI Shapefile")
    inDataSource = inDriver.Open(inShapefile, 0)
    inLayer = inDataSource.GetLayer()
    
    for i in range(0, inLayer.GetFeatureCount()):
        # Get the input Feature
        inFeature = inLayer.GetFeature(i)
        # Create output Feature
        outFeature = ogr.Feature(outLayerDefn)
        temp1 = inFeature.GetField(0)
        # find the row in CSV file which corresponds to the NUTS region obtained from temp1.
        temp2 = np.argwhere(ID==temp1)
        for j in range(len(fieldNames)):
            temp0 = check_null[temp2,j]
            if temp0:
                temp = df[temp2,j][0][0]
                # change str(temp) according to the input file
                outFeature.SetField(outLayerDefn.GetFieldDefn(j).GetNameRef(), temp)
                
        geom = inFeature.GetGeometryRef()
        outFeature.SetGeometry(geom)
        # Add new feature to output Layer
        outLayer.CreateFeature(outFeature)
        inFeature = None
        outFeature = None
    # Save and close DataSources
    inDataSource = None
    outDataSource = None
    
if __name__ == "__main__":
    start = time.time()
    inCSV = "/home/simulant/ag_lukas/personen/Mostafa/ESPON/New_Complete_incl_ISI_final_NUTS0.csv"
    #inCSV = "/home/simulant/ag_lukas/personen/Mostafa/ESPON/Book1.csv"
    inShpPath = "/home/simulant/ag_lukas/personen/Mostafa/ESPON/input.csv.shp"
    outShpPath = "/home/simulant/ag_lukas/personen/Mostafa/ESPON/Data.shp"
    Excel2shapefile(inShpPath, inCSV, outShpPath)
    print(time.time() - start)
    