# -*- coding: utf-8 -*-
"""
Created on July 7 2017

@author: fallahnejad@eeg.tuwien.ac.at
"""
import pandas as pd
import ogr
import osr
import os
import time
import sys


def shp2csv(inShapefile, outCSV):
    # get the input layer
    driver = ogr.GetDriverByName('ESRI Shapefile')
    inDataSet = driver.Open(inShapefile)
    inLayer = inDataSet.GetLayer()
    
    # get projection from Layer
    inSpatialRef = inLayer.GetSpatialRef()
    
    # output SpatialReference
    outSpatialRef = osr.SpatialReference()
    outSpatialRef.ImportFromEPSG(3035)    
    
    # create the CoordinateTransformation
    coordTrans = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)
    
    # add fields
    inLayerDefn = inLayer.GetLayerDefn()
    fieldnames = []
    for i in range(inLayerDefn.GetFieldCount()):
        fieldnames.append(inLayerDefn.GetFieldDefn(i).GetName())
    
    if "ID" and "SDG" and "KGF" and "OBJ" and "GRF" not in fieldnames:
        sys.exit('Error!: The layer must contain "ID", "SDG", "KGF", "OBJ", "GRF" and "demand" fields.')
    
    
    
    ID=[]
    SDG=[] # Status des Gebaedes
    KGF=[] # Gebaedeart
    OBJ=[] # Strvz & HausNr.
    GRF=[] # Gross floorarea
    X=[]
    Y=[]
    

    # loop through the input features
    inFeature = inLayer.GetNextFeature()
    while inFeature:
        # get the input geometry
        geom = inFeature.GetGeometryRef()
        # reproject the geometry
        geom.Transform(coordTrans)
        
        x = geom.Centroid().GetX()
        y = geom.Centroid().GetY()
        
        ID.append(inFeature.GetField(fieldnames.index('ID')))
        GRF.append(inFeature.GetField(fieldnames.index('GRF')))
        KGF.append(inFeature.GetField(fieldnames.index('KGF')))
        SDG.append(inFeature.GetField(fieldnames.index('SDG')))
        temp = inFeature.GetField(fieldnames.index('OBJ'))
        newstr = temp.replace("  ", " ")
        OBJ.append(newstr)
        #OBJ.append(temp)
        X.append(x)
        Y.append(y)
        inFeature = inLayer.GetNextFeature()
    
    if len(ID) != len(set(ID)):
        sys.exit('Error!: IDs must be unique values.')
    
    d = {"ID": ID, "SDG": SDG, "KGF": KGF, "OBJ": OBJ, "GRF": GRF, "X": X, "Y": Y}
    col = ["ID", "SDG", "KGF", "OBJ", "GRF", "X", "Y"]
    df = pd.DataFrame(d)
    df = df[col]
    df = df.sort_values(["ID"])
    df.to_csv(outCSV)
    
    # free up memory
    inDataSet = None
    df = None
    
if __name__ == "__main__":
    start = time.time()
    inShapefile = "/home/simulant/ag_lukas/personen/Mostafa/Frankfurt Buildingblocks/Frankfurt_Buildingblocks.shp"
    outLayerPath = "/home/simulant/ag_lukas/personen/Mostafa/Frankfurt Buildingblocks/Frankfurt_coords.csv"
#     outLayerPath = "/home/simulant/ag_lukas/personen/Mostafa/Wien Buildingblocks/Wien_coords.shp"
#     inShapefile = "/home/simulant/ag_lukas/personen/Mostafa/Wien Buildingblocks/Wien.shp"
    shp2csv(inShapefile, outLayerPath)
    print(time.time() - start)