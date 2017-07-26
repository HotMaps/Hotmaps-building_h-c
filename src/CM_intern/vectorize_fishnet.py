import time
import os
from osgeo import gdal
from osgeo import ogr
from osgeo import osr
from fishnet import main
import numpy as np


def vectorize(inRaster, fishnetSHP, outVector1):
    inRastDatasource = gdal.Open(inRaster)
    transfortm = inRastDatasource.GetGeoTransform()
    xOrigin = transfortm[0]
    yOrigin = transfortm[3]
    pixelWidth = transfortm[1]
    pixelHeight = transfortm[5]
    xMax = xOrigin + pixelWidth * inRastDatasource.RasterXSize
    yMin = yOrigin + pixelHeight * inRastDatasource.RasterYSize
    b = inRastDatasource.GetRasterBand(1)
    arr = b.ReadAsArray()
    main(fishnetSHP, xOrigin, xMax, yMin, yOrigin, abs(pixelHeight), pixelWidth)
    
    inShapefile = fishnetSHP
    Driver = ogr.GetDriverByName('ESRI Shapefile')
    inDataSource = Driver.Open(inShapefile)
    inLayer = inDataSource.GetLayer()
    inLayerDefn = inLayer.GetLayerDefn()
    
    
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(3035)
    # Create the output Layer
    outShapefile = outVector1
    outDriver = ogr.GetDriverByName("ESRI Shapefile")
    # Remove output shapefile if it already exists
    if os.path.exists(outShapefile):
        outDriver.DeleteDataSource(outShapefile)
    outDriver = ogr.GetDriverByName("ESRI Shapefile")
    # Create the output shapefile
    outDataSource = outDriver.CreateDataSource(outShapefile)
    outLayer = outDataSource.CreateLayer("Frankfurt_HDM_V1", srs, geom_type=ogr.wkbPolygon)
    
    
    
    Field = ogr.FieldDefn('HeatDens', ogr.OFTReal)
    outLayer.CreateField(Field)
    outLayerDefn = outLayer.GetLayerDefn()
    (i, j) = arr.shape
    
    
    
    inFeature = inLayer.GetNextFeature()
    while inFeature:
        fid = inFeature.GetFID()
        outFeature = ogr.Feature(outLayerDefn)
        geom = inFeature.GetGeometryRef()
        x = geom.Centroid().GetX()
        y = geom.Centroid().GetY()
        jIndex = int(np.floor((x - xOrigin)/pixelWidth))
        iIndex = int(np.floor((y - yOrigin)/pixelHeight))
        temp = float(arr[iIndex, jIndex])
        if temp > 0:
            outFeature.SetField('HeatDens', temp)
            outFeature.SetGeometry(geom)
            # Add new feature to output Layer
            outLayer.CreateFeature(outFeature)
            outFeature = None
        inFeature = inLayer.GetNextFeature()
    
    inDataSource = None
    outDataSource = None
    
    



if __name__ == "__main__":
    inRaster = "/home/simulant/ag_lukas/personen/Mostafa/Frankfurt Buildingblocks/Frankfurt_ZS_1.tif"
    outVector = "/home/simulant/ag_lukas/personen/Mostafa/Frankfurt Buildingblocks/Frankfurt_Vectorize.shp"
    outVector1 = "/home/simulant/ag_lukas/personen/Mostafa/Frankfurt Buildingblocks/Frankfurt_HDM_V1.shp"
    vectorize(inRaster, outVector, outVector1)