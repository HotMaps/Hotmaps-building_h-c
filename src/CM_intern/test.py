import os
import time
import numpy as np
from osgeo import gdal
from osgeo import ogr
from osgeo import osr
import pandas as pd


def filtering(lyr, filterlyr, outCSV):
    
    fieldList = np.array(['hotmaps_ID', 'Type', 'Area'], dtype=str)
    
    
    driver = ogr.GetDriverByName("ESRI Shapefile")
    lyrDataSource = driver.Open(lyr, 0)
    mainLyr = lyrDataSource.GetLayer()
    
    driver1 = ogr.GetDriverByName("ESRI Shapefile")
    filterlyrDataSource = driver1.Open(filterlyr, 0)
    filterLyr = filterlyrDataSource.GetLayer()
    
    filterG = filterLyr.GetNextFeature()
    filterGeom = filterG.GetGeometryRef()
    mainLyr.SetSpatialFilter(filterGeom)
    
    feat_count = mainLyr.GetFeatureCount()
    fieldvalues = np.empty((feat_count, 3)).astype(int)
    counter = 0
    inFeature = mainLyr.GetNextFeature()
    while inFeature:
        counter = inFeature.GetFID()
        fieldvalues[counter, 0] = str(counter)
        geom = inFeature.GetGeometryRef()
        fieldvalues[counter, 1] = str(inFeature.GetField(4))
        fieldvalues[counter, 2] = str(geom.GetArea())
        inFeature = mainLyr.GetNextFeature()
        counter +=1
     
    df = pd.DataFrame(fieldvalues, columns=fieldList,
                      index=np.arange(feat_count))
    df = df[fieldList]
    #df = df.sort_values(["hotmaps_ID"])
    df.to_csv(outCSV)
    inDataSet = None
    df = None

if __name__ == "__main__":
    start = time.time()
    ly = "/home/simulant/ag_lukas/personen/Mostafa/Frankfurt Buildingblocks/" \
                         "germany_hessen/gis.osm_buildings_a_free_1_3035.shp"
    filterlyr = "/home/simulant/ag_lukas/personen/Mostafa/" \
                "Frankfurt Buildingblocks/Frankfurt.shp"
    outCSV = "/home/simulant/ag_lukas/personen/Mostafa/" \
                "Frankfurt Buildingblocks/Frankfurt_OSM.csv"
    
    
    print(time.time() - start)                     