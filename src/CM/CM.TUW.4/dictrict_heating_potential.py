# -*- coding: utf-8 -*-
"""
Created on July 10 2017

@author: fallahnejad@eeg.tuwien.ac.at
"""
import time
import gdal
import ogr
import osr
import numpy as np
from scipy.ndimage import binary_dilation
from scipy.ndimage import binary_erosion
from scipy.ndimage import binary_fill_holes
from scipy.ndimage import measurements
'''
The input for this calculation module is "heat density map" with [GWh/km2]
unit. The output of this calculation module is set of connected pixels to
which the potential of that connected pixels in [GWh] is assigned.
pixel_threshold in [GWh/km2]
DH_threshold in [GWh/annum]
'''


def array2raster(outRasterPath, rasterOrigin, pixelWidth, pixelHeight,
                 dataType, array, noDataValue):
    '''This function rasterizes the input numpy array '''
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


def DHRegions(DH, DH_threshold):
    '''
    This code uses the concept of connected components from image processing
    library of Scipy in order to detect the potential district heating areas.
    '''
    # "struct" defines how the connected components can be considered.
    struct = np.ones((3, 3)).astype(int)
    # expansion and erosion of the connected components in order to connect
    # different components which are in close vicinity of each other
    # struct(3,3): 200 meter distance between the two connected components
    DH_expanded = binary_dilation(DH, structure=struct)
    DH_connected = binary_erosion(DH_expanded, structure=struct)
    # fills the holes within the connected components
    DH_noHole = binary_fill_holes(DH_connected)
    # label the connected components
    struct = np.ones((3, 3)).astype(int)
    labels, numLabels = measurements.label(DH_noHole, structure=struct)
    # the conditional statement prevents from error in the following code.
    # This can also be incorporated in order to filter areas smaller than a
    # specific size e.g. 1km2 ~ 100.
    if labels.size > 0:
        # labels start from 1. Therefore, PotDH should have numLabels+1
        # elements
        PotDH = np.zeros((numLabels+1)).astype(bool)
        # using sparse matrix indices to swift the calculation. This helps to
        # implement "np.unique" much faster
        sparseRow, sparseCol = np.nonzero(labels)
        sparseLabels = labels[sparseRow, sparseCol]
        sparseDH = DH[sparseRow, sparseCol]
        # sort sparse values based on sparseLabels. This helps to implement
        # summation process much faster.
        sortedSparseData = np.asarray(sorted(zip(sparseRow, sparseCol,
                                                 sparseLabels, sparseDH),
                                             key=lambda x: x[2]))
        # find unique values and their counts within the sparseLabels
        unique, counts = np.unique(sparseLabels, return_counts=True)
        '''
        calculate starting and ending indices of each unique value in order
        to swift the summation operation. calculate starting and ending
        indices of each unique value in order to swift the summation
        operation. Note that a[st:end] refers to elements of a including "st"
        and excluding end.
        Note: To get the last element of the same type, however, cumsum shoud
        be subtracted by 1:
        (e.g. [1,1,1,1,2,2,2]: hear st for 1 is 0; end for 1 is 4; the last
        element which is one is 3)
        '''
        end = np.cumsum(counts)
        st = np.concatenate((np.zeros((1)), end[0:numLabels-1]))
        for i in range(numLabels):
            # sum over sparseDH
            # input: [GWh/km2] for each ha --> to get potential in GWh it
            # should be multiplied by 0.01
            pot = 0.01 * np.sum(sortedSparseData[int(st[i]):int(end[i]), 3])
            if pot >= DH_threshold:
                # here should be i+1 because labeling starts from one and not
                # from zero
                PotDH[i+1] = True
        DH_regions = PotDH[labels]
        return DH_regions


def DHPotential(DH_Regions, HD):
    print("Calculate DH potentials")
    struct = np.ones((3, 3)).astype(int)
    labels, numLabels = measurements.label(DH_Regions, structure=struct)
    DHPot = np.zeros((numLabels+1)).astype(float)
    sparseRow, sparseCol = np.nonzero(labels)
    # This helps to implement "np.unique" much faster
    sparseLabels = labels[sparseRow, sparseCol]
    sparseHD = HD[sparseRow, sparseCol]
    # sort sparse values based on sparseLabels. This helps to implement
    # summation process much faster.
    sortedSparseData = np.asarray(sorted(zip(sparseRow, sparseCol,
                                             sparseLabels, sparseHD),
                                         key=lambda x: x[2]))
    unique, counts = np.unique(sparseLabels, return_counts=True)
    end = np.cumsum(counts)
    st = np.concatenate((np.zeros((1)), end[0:numLabels-1]))
    for i in range(numLabels):
        # input: [GWh/km2] for each ha --> to get potential in GWh it
        # should be multiplied by 0.01
        DHPot[i+1] = 0.01 * np.sum(sortedSparseData[int(st[i]):int(end[i]), 3])
    DH_Potential = DHPot[labels]
    return DH_Potential


def NutsCut(heat_density_map, strd_vector_path, pix_threshold,
            DH_threshold, outRasterPath):
    cutRastDatasource = gdal.Open(heat_density_map)
    transform = cutRastDatasource.GetGeoTransform()
    minx = transform[0]
    maxy = transform[3]
    rasterOrigin = (minx, maxy)
    b11 = cutRastDatasource.GetRasterBand(1)
    arr1 = b11.ReadAsArray().astype(float)
    DH = arr1 * (arr1 > pix_threshold)
    (dimX, dimY) = DH.shape
    DH_Regions = np.zeros((dimX, dimY)).astype(bool)
    inDriver = ogr.GetDriverByName("ESRI Shapefile")
    inDataSource = inDriver.Open(strd_vector_path, 0)
    inLayer = inDataSource.GetLayer()
    fminx = fminy = 10**10
    fmaxx = fmaxy = 0
    flag = 0
    for fid in range(inLayer.GetFeatureCount()):
        print(fid)
        fminx = fminy = 10**10
        fmaxx = fmaxy = 0
        inFeature = inLayer.GetFeature(fid)
        geom = inFeature.GetGeometryRef()
        #Get boundaries
        fminx_, fmaxx_, fminy_, fmaxy_ = geom.GetEnvelope()
        fminx = min(fminx_, fminx)
        fminy = min(fminy_, fminy)
        fmaxx = max(fmaxx_, fmaxx)
        fmaxy = max(fmaxy_, fmaxy)
        # define exact index that encompasses the feature.
        lowIndexY = int((fminx-minx)/100.0)
        lowIndexX = int((maxy-fmaxy)/100.0)
        upIndexY = lowIndexY + int((fmaxx-fminx)/100.0)
        upIndexX = lowIndexX + int((fmaxy-fminy)/100.0)
        while (minx + upIndexY*100) < fmaxx:
            upIndexY = upIndexY + 1
        while (maxy - upIndexX*100) > fminy:
            upIndexX = upIndexX + 1
        # check if input shapefile exceed the boundaries of input raster file.
        if lowIndexY < 0:
            lowIndexY = 0
            flag = 1
        if lowIndexX < 0:
            lowIndexX = 0
            flag = 1
        if upIndexY > dimY:
            upIndexY = dimY
            flag = 1
        if upIndexX > dimX:
            upIndexX = dimX
            flag = 1
        if flag == 1:
            print("Warning: feature '%s' is out of range of the input" \
                  "heat density map" %str(fid))
            flag = 0
        # rasterOrigin2 = (minx + lowIndexY*100, maxy - lowIndexX*100)
        arr_out = DH[lowIndexX:upIndexX, lowIndexY:upIndexY]
        DH_Selected_Region = DHRegions(arr_out, DH_threshold)
        DH_Regions[lowIndexX:upIndexX,
                   lowIndexY:upIndexY] += DH_Selected_Region
        arr_out = None
        inFeature = None
    result = DHPotential(DH_Regions, arr1)
    array2raster(outRasterPath, rasterOrigin, 100, -100, "float32", result, 0)
    cutRastDatasource = None
    arr1 = None


if __name__ == "__main__":
    start = time.time()
    heat_density_map = "/home/simulant/ag_lukas/personen/Mostafa/" \
                       "DHpot/demand_v2_complete.tif"
    strd_vector_path = "/home/simulant/ag_lukas/personen/Mostafa/" \
                       "DHpot/EU28.shp"
    outRasterPath = "/home/simulant/ag_lukas/personen/Mostafa/" \
                    "potDH/Pot_EU28_TH30_1.tif"
    # pix_threshold [GWh/km2]
    pix_threshold = 10
    # DH_threshold [GWh/a]
    DH_threshold = 30
    NutsCut(heat_density_map, strd_vector_path, pix_threshold,
            DH_threshold, outRasterPath)
    elapsed = time.time() - start
    print(elapsed)
