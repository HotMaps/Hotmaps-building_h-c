# -*- coding: utf-8 -*-
"""
Created on July 6 2017

@author: fallahnejad@eeg.tuwien.ac.at
"""
import numpy as np
import pandas as pd
import gdal
import osr
import time
'''
Functions:
- zonStat_selectedArea: Reads a CSV file containing demand values with [kWh]
unit as well as X-Y coordinates in EPSG: 3035 coordinate for each building;
Calculates demand in every 1ha pixel and export a heat density array [GWh/km2]
to the array2raster function.
- array2raster: Gets a numpy array as an input and creates a raster.
'''


def array2raster(outRasterPath, rasterOrigin, pixelWidth, pixelHeight,
                 dataType, array, noDataValue):
    # conversion of data types from numpy to gdal
    # float64 is the default to make sure large values are not missed.
    dict_varTyp = {"int8":      gdal.GDT_Byte,
                   "int16":     gdal.GDT_Int16,
                   "int32":     gdal.GDT_Int32,
                   "uint16":    gdal.GDT_UInt16,
                   "uint32":    gdal.GDT_UInt32,
                   "float32":   gdal.GDT_Float32,
                   "float64":   gdal.GDT_Float64}
    cols = array.shape[1]
    rows = array.shape[0]
    originX = rasterOrigin[0]
    originY = rasterOrigin[1]

    driver = gdal.GetDriverByName('GTiff')
    outRaster = driver.Create(outRasterPath, cols, rows, 1,
                              dict_varTyp[dataType], ['compress=LZW'])
    outRaster.SetGeoTransform((originX, pixelWidth, 0,
                               originY, 0, pixelHeight))
    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromEPSG(3035)
    outRaster.SetProjection(outRasterSRS.ExportToWkt())
    outRaster.GetRasterBand(1).SetNoDataValue(noDataValue)
    outRaster.GetRasterBand(1).WriteArray(array)
    outRaster.FlushCache()


def zonStat_selectedArea(inputCSV, outRasterPath):
    '''
    This function calculates the sum of demand within 100 m pixels.
    The pixel will also overlay to the standard fishnet used for the hotmap
    toolbox since the multiplying factor matches to distances from the origin
    of the standard fishnet. The code assumes a resolution of 100x100 m for the
    output.
    '''
    ifile = pd.read_csv(inputCSV)
    demand = ifile['demand'].values
    X = ifile['X_3035'].values
    Y = ifile['Y_3035'].values
    x0 = 100 * np.floor(np.min(X)/100).astype(int)
    y0 = 100 * np.ceil(np.max(Y)/100).astype(int)
    rasterOrigin = (x0, y0)
    xIndex = np.floor((X-x0)/100.0).astype(int)
    yIndex = np.floor((y0-Y)/100.0).astype(int)
    xWidth = np.max(xIndex) - np.min(xIndex) + 1
    yWidth = np.max(yIndex) - np.min(yIndex) + 1
    index = xIndex + xWidth * yIndex
    # The number of rows of "index" and "demand" must be equal.
    sortedData = np.asarray(sorted(zip(index, demand), key=lambda x: x[0]))
    unique, counts = np.unique(index, return_counts=True)
    end = np.cumsum(counts)
    st = np.concatenate((np.zeros((1)), end[0:end.size-1]))
    # xIndex and yIndex start from 0. So they should be added by 1
    sumDem = np.zeros((np.max(xIndex)+1)*(np.max(yIndex)+1))
    item_location = 0
    for item in unique:
        # sum of demand for each index
        startIndex = int(st[item_location])
        endIndex = int(end[item_location])
        sumDem[item] = np.sum(sortedData[startIndex:endIndex, 1])
        item_location += 1
    '''
    xWidth and yWidth in the following refer to columns and rows,
    respectively and should not wrongly be considered as coordination!
    '''
    # kWh/ha = 10^(-4) * GWh/km2
    sumDem = 0.0001 * sumDem.reshape((yWidth, xWidth))
    array2raster(outRasterPath, rasterOrigin, 100, -100, "float64", sumDem, 0)


if __name__ == "__main__":
    start = time.time()
    inputCSV = "/home/simulant/ag_lukas/personen/Mostafa/Task 3.1/" \
               "NoDemandData/Bistrita.csv"
    outRasterPath = "/home/simulant/ag_lukas/personen/Mostafa/Task 3.1/" \
                    "NoDemandData/Bistrita_HDM_V3.tif"
    zonStat_selectedArea(inputCSV, outRasterPath)

    print(time.time() - start)
