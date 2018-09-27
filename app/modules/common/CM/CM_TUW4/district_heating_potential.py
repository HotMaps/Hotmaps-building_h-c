# -*- coding: utf-8 -*-
"""
Created on July 11 2017

@author: fallahnejad@eeg.tuwien.ac.at
"""
import os
import sys
import time
from osgeo import ogr
import numpy as np
from scipy.ndimage import binary_dilation
from scipy.ndimage import binary_erosion
from scipy.ndimage import binary_fill_holes
from scipy.ndimage import measurements
from docutils.io import InputError
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)
from CM.CM_TUW1.read_raster import read_raster_by_feature as RAbF
import CM.CM_TUW20.run_cm as CM20
'''
The input for this calculation module is "heat density map" with [MWh/ha]
unit. The output of this calculation module is a shapefile showing the
coherent areas with their DH potential.
pixel_threshold in [MWh/ha]
DH_threshold in [GWh/year]
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
    # DH_noHole = binary_fill_holes(DH_connected)
    DH_noHole = DH_connected
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
            # input: [MWh/ha] for each ha --> summation returns MWh for the
            # coherent area
            pot = np.sum(sortedSparseData[int(st[i]):int(end[i]), 3])
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
        # input: [MWh/ha] for each ha --> to get potential in GWh it
        # should be multiplied by 0.001
        DHPot[i+1] = 0.001*np.sum(sortedSparseData[int(st[i]):int(end[i]), 3])
    # remove zero from DHPot
    DHPot = DHPot[1::]
    # potential of each coherent area in GWh is assigned to its pixels
    return DHPot, labels


def DHReg(heat_density_map, strd_vector_path, pix_threshold, DH_threshold,
          in_orig=None):
    # Factor 1000 for conversion from GWh/a to MWh/a
    DH_threshold = DH_threshold * 1000
    flag1 = False
    flag2 = False
    if isinstance(heat_density_map, str):
        arr1, gt = RAbF(strd_vector_path, heat_density_map, return_gt=True)
        minx, maxy = gt[0], gt[3]
        flag1 = True
    elif isinstance(heat_density_map, np.ndarray):
        flag2 = True
    # read vector layer
    inDriver = ogr.GetDriverByName("ESRI Shapefile")
    inDataSource = inDriver.Open(strd_vector_path, 0)
    inLayer = inDataSource.GetLayer()
    if flag2:
        if not in_orig:
            raise TypeError('The raster origin is of None type!')
        minx, maxy = in_orig[0], in_orig[1]
        shp_minX, shp_maxX, shp_minY, shp_maxY = inLayer.GetExtent()
        (dimX0, dimY0) = heat_density_map.shape
        (lowIndexX, upIndexX, lowIndexY, upIndexY) = CM20.main(minx, maxy,
                                                               dimX0, dimY0,
                                                               shp_minX, shp_maxX,
                                                               shp_minY, shp_maxY)
        minx = minx + 100 * lowIndexY
        maxy = maxy - 100 * lowIndexX
        arr1 = heat_density_map[lowIndexX:upIndexX, lowIndexY:upIndexY]
    if not (flag1 or flag2):
        raise InputError('The heat density map/array is not valid!')
    rasterOrigin = (minx, maxy)
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
    heat_density_map = data_warehouse + os.sep + 'heat_tot_curr_density_AT.tif'
    region = data_warehouse + os.sep + 'AT.shp'
    output_dir = path + os.sep + 'Outputs'
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    outRasterPath = output_dir + os.sep + 'Pot_AT_TH30.tif'
    # pix_threshold [MWh/ha]
    pix_threshold = 100
    # DH_threshold [GWh/a]
    DH_threshold = 30
    output = DHReg(heat_density_map, region, pix_threshold, DH_threshold)
    elapsed = time.time() - start
    print("%0.3f seconds" % elapsed)
