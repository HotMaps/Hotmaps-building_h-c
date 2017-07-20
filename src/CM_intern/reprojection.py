import os
import time
from osgeo import ogr
from osgeo import osr
import pandas as pd


def reproject(inShapefile, outLayerPath):
# set geometry type before you run the program: wkbLineString, wkbPolygon, ...
    
    driver = ogr.GetDriverByName('ESRI Shapefile')

    # input SpatialReference
    inSpatialRef = osr.SpatialReference()
    inSpatialRef.ImportFromEPSG(4258)

    # output SpatialReference
    outSpatialRef = osr.SpatialReference()
    outSpatialRef.ImportFromEPSG(3035)

    # create the CoordinateTransformation
    coordTrans = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)

    # get the input layer
    inDataSet = driver.Open(inShapefile)
    inLayer = inDataSet.GetLayer()

    # create the output layer
    outputShapefile = outLayerPath
    if os.path.exists(outputShapefile):
        driver.DeleteDataSource(outputShapefile)
    outDataSet = driver.CreateDataSource(outputShapefile)
    outLayer = outDataSet.CreateLayer("Frankfurt", outSpatialRef, geom_type=ogr.wkbPolygon)
    

    # add fields
    inLayerDefn = inLayer.GetLayerDefn()
    for i in range(0, inLayerDefn.GetFieldCount()):
        fieldDefn = inLayerDefn.GetFieldDefn(i)
        outLayer.CreateField(fieldDefn)
    
    
    # get the output layer's feature definition
    outLayerDefn = outLayer.GetLayerDefn()

    # loop through the input features
    inFeature = inLayer.GetNextFeature()
    while inFeature:
        # get the input geometry
        geom = inFeature.GetGeometryRef()
        x = geom.Centroid().GetX()
        y = geom.Centroid().GetY()
        # reproject the geometry
        geom.Transform(coordTrans)
        # create a new feature
        outFeature = ogr.Feature(outLayerDefn)
        # set the geometry and attribute
        outFeature.SetGeometry(geom)
        for i in range(0, outLayerDefn.GetFieldCount()):
            outFeature.SetField(outLayerDefn.GetFieldDefn(i).GetNameRef(), inFeature.GetField(i))
        # add the feature to the shapefile
        outLayer.CreateFeature(outFeature)
        # dereference the features and get the next input feature
        outFeature = None

        inFeature = inLayer.GetNextFeature()
    

    
    # Save and close the shapefiles
    inDataSet = None
    outDataSet = None
    
if __name__ == "__main__":
    start = time.time()
    layers = ['NUTS_BN_01M_2013']
    inputFolder = "/home/simulant/ag_lukas/personen/Mostafa/Frankfurt Buildingblocks/"
    outputFolder = "/home/simulant/ag_lukas/personen/Mostafa/Frankfurt Buildingblocks/"
    for i in range(len(layers)):
        inShapefile = inputFolder + layers[i] + '.shp'
        outLayerPath = outputFolder + layers[i] + '_3035.shp'
        reproject(inShapefile, outLayerPath)
    print(time.time() - start)