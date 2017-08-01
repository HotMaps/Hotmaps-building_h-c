# -*- coding: utf-8 -*-
"""
Created on July 26 2017

@author: fallahnejad@eeg.tuwien.ac.at
"""
import os
import sys
import time
import numpy as np
from osgeo import gdal
from osgeo import osr
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)
'''
This function rasterizes the input numpy array. The input array and the
geo_transform must be given for EPSG3035.
'''


def array2raster(outRasterPath, geo_transform, dataType, array, noDataValue=0,
                 OutputRasterSRS=3035):
    # conversion of data types from numpy to gdal
    dict_varTyp = {"int8":      gdal.GDT_Byte,
                   "int16":     gdal.GDT_Int16,
                   "int32":     gdal.GDT_Int32,
                   "uint16":    gdal.GDT_UInt16,
                   "uint32":    gdal.GDT_UInt32,
                   "float32":   gdal.GDT_Float32,
                   "float64":   gdal.GDT_Float64}
    cols = array.shape[1]
    rows = array.shape[0]
    driver = gdal.GetDriverByName('GTiff')
    outRaster = driver.Create(outRasterPath, cols, rows, 1,
                              dict_varTyp[dataType], ['compress=LZW'])
    outRaster.SetGeoTransform(geo_transform)
    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromEPSG(OutputRasterSRS)
    outRaster.SetProjection(outRasterSRS.ExportToWkt())
    outRaster.GetRasterBand(1).SetNoDataValue(noDataValue)
    outRaster.GetRasterBand(1).WriteArray(array)
    outRaster.FlushCache()


if __name__ == "__main__":
    start = time.time()
    output_dir = path + os.sep + 'Outputs'
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    outRasterPath = output_dir + os.sep + 'array2raster.tif'
    array = np.ones((50, 20))
    dataType = 'float32'
    geo_transform = (4285400, 100, 0, 2890500, 0, -100)
    noDataValue = 0
    array2raster(outRasterPath, geo_transform, dataType, array, noDataValue)
    elapsed = time.time() - start
    print("%0.3f seconds" %elapsed)

