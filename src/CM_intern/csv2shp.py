# -*- coding: utf-8 -*-
"""
Created on Thu May 4 2017

@author: Mostafa
"""
import os
import time
import numpy as np
from osgeo import ogr
from osgeo import osr
import pandas as pd
# from asyncio.windows_events import NULL
'''
inputs:
    inShpPath:    path to the input shp file
    inCSV:        path to the input csv file or Pandas DataFrame
    outShpPath:   path for saving the output shp
'''


def Excel2shapefile(inShpPath, inCSV, outShpPath, OutputSRS=3035):
    # read the input shapefile
    inShapefile = inShpPath
    inDriver = ogr.GetDriverByName("ESRI Shapefile")
    inDataSource = inDriver.Open(inShapefile, 0)
    inLayer = inDataSource.GetLayer()
    # set CRS
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(OutputSRS)
    # Create the output Layer
    outShapefile = outShpPath
    outDriver = ogr.GetDriverByName("ESRI Shapefile")
    # Remove output shapefile if it already exists
    if os.path.exists(outShapefile):
        outDriver.DeleteDataSource(outShapefile)
    outDriver = ogr.GetDriverByName("ESRI Shapefile")
    # Create the output shapefile
    outDataSource = outDriver.CreateDataSource(outShapefile)
    geom_typ = inLayer.GetGeomType()
    geom_typ_dict = {1: ogr.wkbPoint, 2: ogr.wkbLineString, 3: ogr.wkbPolygon}
    outLayer = outDataSource.CreateLayer("NUTS_Demand", srs,
                                         geom_type=geom_typ_dict[geom_typ])
    if isinstance(inCSV, str):
        # read CSV file
        ifile = pd.read_csv(inCSV)
    else:
        ifile = inCSV
    df = ifile.values
    ID = ifile['id']
    check_null = ifile.notnull().values
    # read the headers (first row of each column)
    fieldNames = ifile.columns.values
    '''
    ogr field types definition:
    OFTInteger=0, OFTIntegerList=1, OFTReal=2, OFTRealList=3,
    OFTString=4, OFTStringList=5, OFTWideString=6, OFTWideStringList=7,
    OFTBinary=8, OFTDate=9, OFTTime=10, OFTDateTime=11,
    OFTInteger64=12, OFTInteger64List=13, OFTMaxType=13
    '''
    dict_ogr_dtypes = {np.dtype('O'): 4,
                       np.dtype('int64'): 12,
                       np.dtype('float64'): 2}
    for i, item in enumerate(fieldNames):
        # if key does not exist, the column will be considered as string
        Field = ogr.FieldDefn(fieldNames[i],
                              dict_ogr_dtypes.get(ifile[item].dtypes, 4))
        outLayer.CreateField(Field)
    # Get the output Layer's Feature Definition
    outLayerDefn = outLayer.GetLayerDefn()
    for i in range(0, inLayer.GetFeatureCount()):
        # Get the input Feature
        inFeature = inLayer.GetFeature(i)
        # Create output Feature
        outFeature = ogr.Feature(outLayerDefn)
        temp1 = inFeature.GetField(0)
        # find the row in CSV file which corresponds to the NUTS region
        # obtained from temp1.
        temp2 = np.argwhere(ID == temp1)
        for j in range(len(fieldNames)):
            temp0 = check_null[temp2, j]
            if temp0:
                temp = df[temp2, j][0][0]
                # change str(temp) according to the input file
                outFeature.SetField(outLayerDefn.GetFieldDefn(j).GetNameRef(),
                                    temp)
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
    inCSV = "/home/simulant/ag_lukas/personen/Mostafa/ESPON/New_Complete_incl_ISI_final.csv"
    #inCSV = "/home/simulant/ag_lukas/personen/Mostafa/ESPON/Book1.csv"
    inShpPath = "/home/simulant/ag_lukas/personen/Mostafa/ESPON/input.csv.shp"
    outShpPath = "/home/simulant/ag_lukas/personen/Mostafa/ESPON/Data.shp"
    Excel2shapefile(inShpPath, inCSV, outShpPath)
    print(time.time() - start)
