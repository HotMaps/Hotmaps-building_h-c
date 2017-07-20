# -*- coding: utf-8 -*-
"""
Created on Fri Jun  2 15:21:48 2017

@author: Mostafa
"""

import numpy as np
from osgeo import gdal
from osgeo import ogr
from osgeo import osr


def test(x0, y0, col, row):
    x = (x0 + np.arange(col)*100)
    y = (y0 - np.arange(row)*100)
    X = np.repeat(x,row)
    Y = np.repeat(y,col).reshape(row,col).flatten('F')
    res = np.dstack((X,Y))[0]
    multipoint = ogr.Geometry(ogr.wkbMultiPoint)
    point = ogr.Geometry(ogr.wkbPoint)
    for item in res:
        point.AddPoint(float(item[0]),float(item[1]))
        multipoint.AddGeometry(point)
    path = "/home/simulant/ag_lukas/personen/Mostafa/Wien Buildingblocks/NUTS3.shp"
    driver = ogr.GetDriverByName('ESRI Shapefile')
    inDataSet = driver.Open(path)
    inLayer = inDataSet.GetLayer()
    multipoint.SetSpatialFilter(inLayer)
    print(multipoint.ExportToWkt)


if __name__ == "__main__":
    test(944000, 5414000, 55590, 44720)    