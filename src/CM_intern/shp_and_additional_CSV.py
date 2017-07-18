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

def Excel2shapefile(inLayerPath, inCSV, outLayerPath):
    ifile = pd.read_csv(inCSV)
    df = ifile.values
    ID = ifile['OBJECTID']
    check_null = pd.read_csv(inCSV).notnull().values
    # read the headers (first row of each column)
    fieldNames = pd.read_csv(inCSV, nrows=1).columns.values
    
    # Check for correct inputs
    if not (inLayerPath[-4:]==".shp" and outLayerPath[-4:]==".shp"):
        print("wrong input/output layers!")
        return
    
    
    
    # Get the input Layer
    inShapefile = inLayerPath
    inDriver = ogr.GetDriverByName("ESRI Shapefile")
    inDataSource = inDriver.Open(inShapefile, 0)
    inLayer = inDataSource.GetLayer()
    
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(3035)
    
    # Create the output Layer
    outShapefile = outLayerPath
    outDriver = ogr.GetDriverByName("ESRI Shapefile")

    # Remove output shapefile if it already exists
    if os.path.exists(outShapefile):
        outDriver.DeleteDataSource(outShapefile)

    # Create the output shapefile
    outDataSource = outDriver.CreateDataSource(outShapefile)
    outLayer = outDataSource.CreateLayer("newSHP", srs, geom_type=ogr.wkbPolygon)
    
    # Add input Layer Fields to the output Layer
    inLayerDefn = inLayer.GetLayerDefn()
    
    field_offset = inLayerDefn.GetFieldCount()
        
    for i in range(0, field_offset):
        fieldDefn = inLayerDefn.GetFieldDefn(i)
        outLayer.CreateField(fieldDefn)
    for i in range(1,len(fieldNames)):
        Field = ogr.FieldDefn(fieldNames[i], ogr.OFTReal)
        outLayer.CreateField(Field)
    
    
    
    # Get the output Layer's Feature Definition
    outLayerDefn = outLayer.GetLayerDefn()
    
    
    
    
    
    for i in range(0, inLayer.GetFeatureCount()):
        # Get the input Feature
        inFeature = inLayer.GetFeature(i)
        # Create output Feature
        outFeature = ogr.Feature(outLayerDefn)
        temp1 = inFeature.GetField(0)
        # find the row in CSV file which corresponds to the NUTS region obtained from temp1.
        temp2 = np.argwhere(ID==temp1)
        for j in range(field_offset):
            outFeature.SetField(outLayerDefn.GetFieldDefn(j).GetNameRef(), inFeature.GetField(j))
        for k in range(1, len(fieldNames)):
            temp0 = check_null[temp2,k]
            if temp0:
                temp = df[temp2,k][0][0]
                # change str(temp) according to the input file
                outFeature.SetField(outLayerDefn.GetFieldDefn(field_offset+k - 1).GetNameRef(), temp)
                
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
    inCSV = "/home/simulant/ag_lukas/personen/Mostafa/Frankfurt Buildingblocks/New Frankfurt SHP/Frankfurt_SHP_Buildings2.csv"
    inShpPath = "/home/simulant/ag_lukas/personen/Mostafa/Frankfurt Buildingblocks/SHP/Frankfurt_Buildingblocks.shp"
    outShpPath = "/home/simulant/ag_lukas/personen/Mostafa/Frankfurt Buildingblocks/New Frankfurt SHP/Frankfurt_Buildingblocks_New.shp"
    Excel2shapefile(inShpPath, inCSV, outShpPath)
    print(time.time() - start)
    