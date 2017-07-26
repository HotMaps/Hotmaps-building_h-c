# -*- coding: utf-8 -*-
"""
Created on July 11 2017

@author: fallahnejad@eeg.tuwien.ac.at
"""
import os
import sys
import time
from osgeo import gdal
from osgeo import ogr
import numpy as np
from scipy.ndimage import binary_dilation
from scipy.ndimage import binary_erosion
from scipy.ndimage import binary_fill_holes
from scipy.ndimage import measurements
path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if path not in sys.path:
    sys.path.append(path)
import CM.CM_TUW20.run_cm as CM20
from AD.heat_density_map.main import HDMAP
'''
The input for this calculation module is "heat density map" with [GWh/km2]
unit. The output of this calculation module is set of connected pixels to
which the potential of that connected pixels in [GWh] is assigned.
pixel_threshold in [GWh/km2]
DH_threshold in [GWh/annum]
'''
verbose = False


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
    if verbose:
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


def DHReg(heat_density_map, strd_vector_path, pix_threshold, DH_threshold):
    inDriver = ogr.GetDriverByName("ESRI Shapefile")
    inDataSource = inDriver.Open(strd_vector_path, 0)
    inLayer = inDataSource.GetLayer()
    shp_minX, shp_maxX, shp_minY, shp_maxY = inLayer.GetExtent()
    cutRastDatasource = gdal.Open(heat_density_map)
    transform = cutRastDatasource.GetGeoTransform()
    minx = transform[0]
    maxy = transform[3]
    b11 = cutRastDatasource.GetRasterBand(1)
    arr1 = b11.ReadAsArray().astype(float)
    (dimX0, dimY0) = arr1.shape
    (lowIndexX, upIndexX, lowIndexY, upIndexY) = CM20.main(minx, maxy,
                                                            dimX0, dimY0,
                                                            shp_minX, shp_maxX,
                                                            shp_minY, shp_maxY)
    minx = minx + 100 * lowIndexY
    maxy = maxy - 100 * lowIndexX
    rasterOrigin = (minx, maxy)
    arr1 = arr1[lowIndexX:upIndexX, lowIndexY:upIndexY]
    DH = arr1 * (arr1 > pix_threshold)
    (dimX, dimY) = DH.shape
    DH_Regions = np.zeros((dimX, dimY)).astype(bool)
    for fid in range(inLayer.GetFeatureCount()):
        if verbose:
            print(fid)
        inFeature = inLayer.GetFeature(fid)
        geom = inFeature.GetGeometryRef()
        # Get boundaries
        fminx, fmaxx, fminy, fmaxy = geom.GetEnvelope()
        # define exact index that encompasses the feature.
        (lowIndexX, upIndexX, lowIndexY, upIndexY) = CM20.main(minx, maxy,
                                                                dimX, dimY,
                                                                fminx, fmaxx,
                                                                fminy, fmaxy)
        # rasterOrigin2 = (minx + lowIndexY*100, maxy - lowIndexX*100)
        arr_out = DH[lowIndexX:upIndexX, lowIndexY:upIndexY]
        DH_Selected_Region = DHRegions(arr_out, DH_threshold)
        DH_Regions[lowIndexX:upIndexX,
                   lowIndexY:upIndexY] += DH_Selected_Region
        arr_out = None
        inFeature = None
    return DH_Regions, arr1, rasterOrigin


if __name__ == "__main__":
    start = time.time()
    data_warehouse = path + os.sep + 'AD/data_warehouse'
    heat_density_map = HDMAP(data_warehouse)
    region = data_warehouse + os.sep + 'AT.shp'
    output_dir = path + os.sep + 'Outputs'
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    outRasterPath = output_dir + os.sep + 'Pot_AT_TH30.tif'
    # pix_threshold [GWh/km2]
    pix_threshold = 10
    # DH_threshold [GWh/a]
    DH_threshold = 30
    output = DHReg(heat_density_map, region, pix_threshold, DH_threshold)
    elapsed = time.time() - start
    print("%0.3f seconds" % elapsed)
