# -*- coding: utf-8 -*-
"""
Created on July 6 2017

@author: fallahnejad@eeg.tuwien.ac.at
"""
from docutils.io import InputError
import os
import sys
import numpy as np
import pandas as pd
import time
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)
import CM.CM_TUW19.run_cm as CM19

'''
Functions:
- zonStat_selectedArea: Reads a CSV file containing demand values with [kWh]
unit as well as X-Y coordinates in EPSG: 3035 coordinate for each building;
Calculates demand in every 1ha pixel and export a heat density array [GWh/km2]
to the array2raster function.
'''


def zonStat_selectedArea(inputCSV, outRasterPath, population=0,
                         resolution=100):
    '''
    This function calculates the sum of demand within a pixels with given
    resolution. The pixel will also overlay to the standard fishnet used for
    the hotmaps toolbox since the multiplying factor matches to distances from
    the origin of the standard fishnet. The code assumes a resolution of
    100x100 m for the output.
    annual building demand must be in kWh/a
    output heat density map raster is in MWh/ha
    '''
    if isinstance(inputCSV, pd.DataFrame):
        ifile = inputCSV
    else:
        if not os.path.isfile(inputCSV):
            raise InputError('The input csv file does not exist!')
        ifile = pd.read_csv(inputCSV)
    demand = ifile['demand'].values
    GFA = ifile['GFA'].values
    X = ifile['X_3035'].values
    Y = ifile['Y_3035'].values
    x0 = resolution * np.floor(np.min(X)/resolution).astype(int)
    y0 = resolution * np.ceil(np.max(Y)/resolution).astype(int)
    rasterOrigin = (x0, y0)
    xIndex = np.floor((X-x0)/resolution).astype(int)
    yIndex = np.floor((y0-Y)/resolution).astype(int)
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
    # kWh/ha = 10^(-3) * MWh/ha
    sumDem = 0.001 * sumDem.reshape((yWidth, xWidth))
    geo_transform = [rasterOrigin[0], resolution, 0
                     , rasterOrigin[1], 0, -resolution]
    CM19.main(outRasterPath, geo_transform, str(sumDem.dtype), sumDem)
    abs_heat_demand = np.sum(demand)
    if np.sum(GFA):
        mean_spec_demand = abs_heat_demand/np.sum(GFA)
    else:
        mean_spec_demand = np.nan
    if population:
        mean_dem_perCapita = abs_heat_demand/float(population)
    else:
        mean_dem_perCapita = np.nan
#     print("Absolute heat demand: %0.1f GWh\a"
#           "Mean heat demand per capita: %0.2f kWh\n"
#           "Mean heat demand per heated surface (ave. specific demand): %0.2f"
#           " kWh/m2"
#           % (abs_heat_demand*10**(-6), mean_dem_perCapita, mean_spec_demand))
    return (abs_heat_demand*10**(-6), mean_dem_perCapita, mean_spec_demand)


if __name__ == "__main__":
    start = time.time()
    output_dir = path + os.sep + 'Outputs'
    col = ['demand', 'GFA', 'X_3035', 'Y_3035']
    data = np.array([[1000, 100, 4795000, 28073000]])
    inputCSV = pd.DataFrame(data, columns=col)
    outRasterPath = output_dir + os.sep + 'CM9_Heat_Density_Map.tif'
    zonStat_selectedArea(inputCSV, outRasterPath)
    print(time.time() - start)
