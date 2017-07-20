import pandas as pd
import numpy as np
from osgeo import ogr
from osgeo import osr
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
  
    
    
    ID=[]
    SDG=[] # Status des Gebaedes
    KGF=[] # Gebaedeart
    OBJ=[] # Strvz & HausNr.
    Footprint=[] # Grundflaeche = Net floor area
    NrFloor = [] # Number of floors
    GFA = [] # Gross floor area
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
        
        ID.append(inFeature.GetField(fieldnames.index('OBJECTID')))
        # Grundflaeche = Net floor area
        Footprint.append(inFeature.GetField(fieldnames.index('GRF')))
        # AOG: number of floors above ground floor  > NRF = 1 + AOG
        NrFloor.append(inFeature.GetField(fieldnames.index('AOG')))
        KGF.append(inFeature.GetField(fieldnames.index('KGF_WERT')))
        SDG.append(inFeature.GetField(fieldnames.index('SDG_WERT')))
        temp = inFeature.GetField(fieldnames.index('LAGE_WERT'))
        newstr = temp.replace("  ", " ")
        OBJ.append(newstr)
        #OBJ.append(temp)
        X.append(x)
        Y.append(y)
        inFeature = inLayer.GetNextFeature()
    NrFloorTemp = np.array(NrFloor)
    #NrFloorTemp[np.argwhere(NrFloorTemp==0)] = 1
    NrFloor = NrFloorTemp.tolist()
    GFA = (np.array(Footprint) * np.array(NrFloor)).tolist()
    d = {"ID": ID, "SDG": SDG, "KGF": KGF, "OBJ": OBJ, "Footprint": Footprint, "NrFloor": NrFloor, "GFA": GFA, "X": X, "Y": Y}
    col = ["ID", "SDG", "KGF", "OBJ", "Footprint", "NrFloor", "GFA", "X", "Y"]
    df = pd.DataFrame(d)
    df = df[col]
    df.to_csv(outCSV)
    
    # Save and close the shapefiles
    inDataSet = None
    outDataSet = None
    
if __name__ == "__main__":
    start = time.time()
    inShapefile = "/home/simulant/ag_lukas/personen/Mostafa/Frankfurt Buildingblocks/Frankfurt_Buildingblocks.shp"
    outLayerPath = "/home/simulant/ag_lukas/personen/Mostafa/Frankfurt Buildingblocks/Frankfurt_coords.csv"
#     outLayerPath = "/home/simulant/ag_lukas/personen/Mostafa/Wien Buildingblocks/Wien_coords.shp"
#     inShapefile = "/home/simulant/ag_lukas/personen/Mostafa/Wien Buildingblocks/Wien.shp"
    shp2csv(inShapefile, outLayerPath)
    print(time.time() - start)