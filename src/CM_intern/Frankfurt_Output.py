import numpy as np
import pandas as pd
import gdal
import osr
import time



def array2raster_multiband(outRasterPath, rasterOrigin, pixelWidth, pixelHeight, dataType, array, noDataValue):
    # conversion of data types from numpy to gdal
    
    dict_varTyp = {
                   "int8":      gdal.GDT_Byte,
                   "int16":     gdal.GDT_Int16,
                   "int32":     gdal.GDT_Int32,
                   "uint16":    gdal.GDT_UInt16,
                   "uint32":    gdal.GDT_UInt32,
                   "float32":   gdal.GDT_Float32,
                   "float64":   gdal.GDT_Float64
                   }
    cols = array.shape[1]
    rows = array.shape[0]
    originX = rasterOrigin[0]
    originY = rasterOrigin[1]
    if len(array.shape) == 3:
        number_of_bands = array.shape[2]
    else:
        number_of_bands = 1
    
    
    driver = gdal.GetDriverByName('GTiff')
    outRaster = driver.Create(outRasterPath, cols, rows, number_of_bands, dict_varTyp[dataType], ['compress=LZW'])
    outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromEPSG(3035)
    outRaster.SetProjection(outRasterSRS.ExportToWkt())
    for band in range(1, 1+ number_of_bands):
        outBand = outRaster.GetRasterBand(band)
        outBand.SetNoDataValue(noDataValue)
        if number_of_bands >1:
            outBand.WriteArray(array[:,:,band-1])
        else:
            outBand.WriteArray(array)
    outRaster.FlushCache()


def newStat(X, Y, inArr, method, outRasterPath):    
    n = 1
    x0 = 100 * np.floor(np.min(X)/100).astype(int)
    y0 = 100 * np.ceil(np.max(Y)/100).astype(int)
    rasterOrigin = (x0, y0)
    xIndex = np.floor((X-x0)/100.0).astype(int)
    yIndex = np.floor((y0-Y)/100.0).astype(int)
    xWidth = np.max(xIndex) - np.min(xIndex) + 1
    yWidth = np.max(yIndex) - np.min(yIndex) + 1
    index = xIndex + xWidth * yIndex
    #sortedData = np.asarray(sorted(np.vstack((index, inArr)),key=lambda x:x[0])) 
    sortedData = np.asarray(sorted(zip(index, inArr),key=lambda x:x[0]))
    unique, counts = np.unique(index, return_counts=True)
    end = np.cumsum(counts)
    st = np.concatenate((np.zeros((1)), end[0:end.size-1]))
    # xIndex and yIndex start from 0. So they should be added by 1
    sumDem = np.zeros(((np.max(xIndex)+1)*(np.max(yIndex)+1), n))
    item_location = 0
    for item in unique:
        # sum of demand for each index
        startIndex = int(st[item_location])
        endIndex = int(end[item_location])
        for i in range(n):
            if method:
                sumDem[item, i] = np.sum(sortedData[startIndex:endIndex, i+1])
            else:
                temp = sortedData[startIndex:endIndex, i+1]
                temp1 = np.nonzero(temp)
                sumDem[item, i] = np.average(temp[temp1])
        item_location += 1
    sumDem = sumDem.reshape((yWidth, xWidth, n))
    array2raster_multiband(outRasterPath, rasterOrigin, 100, -100, "float64", sumDem[:,:,0], 0)



def zonStat_selectedArea(inputCSV, outRasterPath):
    '''
    This function calculates the sum of demand within 100 m pixels.
    The pixel will also overlay to the standard fishnet used for the hotmap toolbox since
    the multiplying factor matches to distances from the origin of the standard fishnet.
    The code assumes a resolution of 100x100 m for the output.
    '''
    ifile = pd.read_csv(inputCSV)
    GArt =  ifile['GArt'].values.astype(int)
    demand0 = ifile['Orig_Dem_KGF'].values.astype(float)
    demand1 = ifile['Orig_Dem_KGF_with_Match'].values.astype(float)
    demand2 = ifile['Orig_Dem_Access'].values.astype(float)
    demand3 = ifile['Dem_KGF'].values.astype(float)
    demand4 = ifile['Dem_KGF_with_Match'].values.astype(float)
    demand5 = ifile['Dem_Access'].values.astype(float)
    spd0 = ifile['Orig_Spec_Dem_KGF'].values.astype(float)
    spd1 = ifile['Orig_Spec_Dem_Access'].values.astype(float)
    spd2 = ifile['Spec_Dem_KGF'].values.astype(float)
    spd3 = ifile['Spec_Dem_Access'].values.astype(float)
    NrFloor_SHP =  ifile['NrFloor_SHP'].values.astype(int)
    NrFloor_Access =  ifile['NrFloor_Access'].values.astype(int)
    Footprint_SHP = ifile['Footprint_SHP'].values.astype(float)
    Footprint_Access = ifile['Footprint_Access'].values.astype(float)
    GrossFloor_SHP = ifile['GrossFloor_SHP'].values.astype(float)
    GrossFloor_Access = ifile['GrossFloor_Access'].values.astype(float)
    X = ifile['X'].values
    Y = ifile['Y'].values
    
    residential = (GArt<5) & (GArt>0)
    non_res = (GArt<1) | (GArt>4)
    X_res = X[residential]
    Y_res = Y[residential]
    X_nonRes = X[non_res]
    Y_nonRes = Y[non_res]
    X_floors_shp = X[NrFloor_SHP>0]
    Y_floors_shp = Y[NrFloor_SHP>0]
    X_floors_Access = X[NrFloor_Access>0]
    Y_floors_Access = Y[NrFloor_Access>0]
    
    nonRes_dem0 = demand0[non_res]
    nonRes_dem1 = demand1[non_res]
    nonRes_dem2 = demand2[non_res]
    nonRes_dem3 = demand3[non_res]
    nonRes_dem4 = demand4[non_res]
    nonRes_dem5 = demand5[non_res]
    
    res_dem0 = demand0[residential]
    res_dem1 = demand1[residential]
    res_dem2 = demand2[residential]
    res_dem3 = demand3[residential]
    res_dem4 = demand4[residential]
    res_dem5 = demand5[residential]
    
    
    res_spd0 = spd0[residential] 
    res_spd1 = spd1[residential]
    res_spd2 = spd2[residential]
    res_spd3 = spd3[residential]
    nonRes_spd0 = spd0[non_res] 
    nonRes_spd1 = spd1[non_res]
    nonRes_spd2 = spd2[non_res]
    nonRes_spd3 = spd3[non_res]
    
    
    NrFloor_SHP_noZero = NrFloor_SHP[NrFloor_SHP>0]
    NrFloor_Access_noZero = NrFloor_Access[NrFloor_Access>0]
    
    
    
    '''
    n = 6
    method = 1
    x0 = 100 * np.floor(np.min(X)/100).astype(int)
    y0 = 100 * np.ceil(np.max(Y)/100).astype(int)
    rasterOrigin = (x0, y0)
    xIndex = np.floor((X-x0)/100.0).astype(int)
    yIndex = np.floor((y0-Y)/100.0).astype(int)
    xWidth = np.max(xIndex) - np.min(xIndex) + 1
    yWidth = np.max(yIndex) - np.min(yIndex) + 1
    index = xIndex + xWidth * yIndex
    #sortedData = np.asarray(sorted(np.vstack((index, inArr)),key=lambda x:x[0])) 
    sortedData = np.asarray(sorted(zip(index, demand0, demand1, demand2, demand3, demand4, demand5),key=lambda x:x[0]))
    unique, counts = np.unique(index, return_counts=True)
    end = np.cumsum(counts)
    st = np.concatenate((np.zeros((1)), end[0:end.size-1]))
    # xIndex and yIndex start from 0. So they should be added by 1
    sumDem = np.zeros(((np.max(xIndex)+1)*(np.max(yIndex)+1), n))
    item_location = 0
    for item in unique:
        # sum of demand for each index
        startIndex = int(st[item_location])
        endIndex = int(end[item_location])
        for i in range(n):
            if method:
                sumDem[item, i] = np.sum(sortedData[startIndex:endIndex, i+1])
            else:
                temp = sortedData[startIndex:endIndex, i+1]
                temp1 = np.nonzero(temp)
                sumDem[item, i] = np.average(temp[temp1])
        item_location += 1
    sumDem = sumDem.reshape((yWidth, xWidth, n))
    array2raster_multiband(outRasterPath+'demand_multiband.tif', rasterOrigin, 100, -100, "float64", sumDem, 0)
    '''
    
    
    
    
    
    
    
    
    
    
    
    
    
    inArr = [demand0, demand1, demand2, demand3, demand4, demand5]
    for i, array in enumerate(inArr):
        newStat(X, Y, array, 1, outRasterPath+'Demand'+str(i)+'.tif')
        
    inArr = [res_dem0, res_dem1, res_dem2, res_dem3, res_dem4, res_dem5]
    for i, array in enumerate(inArr):
        newStat(X_res, Y_res, array, 1, outRasterPath+'Res_Demand'+str(i)+'.tif')    
    
    inArr = [nonRes_dem0, nonRes_dem1, nonRes_dem2, nonRes_dem3, nonRes_dem4, nonRes_dem5]
    for i, array in enumerate(inArr):
        newStat(X_nonRes, Y_nonRes, array, 1, outRasterPath+'nonRes_Demand'+str(i)+'.tif')
    
    inArr = [Footprint_SHP, Footprint_Access, GrossFloor_SHP, GrossFloor_Access]
    for i, array in enumerate(inArr):
        newStat(X, Y, array, 1, outRasterPath+'FloorArea'+str(i)+'.tif')
    
    inArr = [spd0, spd1, spd2, spd3]
    for i, array in enumerate(inArr):
        newStat(X, Y, array, 0, outRasterPath+'Spec_Demand'+str(i)+'.tif')
    
    inArr = [res_spd0, res_spd1, res_spd2, res_spd3]
    for i, array in enumerate(inArr):
        newStat(X_res, Y_res, array, 0, outRasterPath+'Spec_Res_Demand'+str(i)+'.tif')
    
    inArr = [nonRes_spd0, nonRes_spd1, nonRes_spd2, nonRes_spd3]
    for i, array in enumerate(inArr):
        newStat(X_nonRes, Y_nonRes, array, 0, outRasterPath+'Spec_nonRes_Demand'+str(i)+'.tif')   
    
    inArr = [NrFloor_SHP]
    for i, array in enumerate(inArr):
        newStat(X, Y, array, 0, outRasterPath+'Average_NrFloors_SHP.tif') 
    
    inArr = [NrFloor_Access]
    for i, array in enumerate(inArr):
        newStat(X[NrFloor_Access>=0], Y[NrFloor_Access>=0], array, 0, outRasterPath+'Average_NrFloors_Access.tif')
     
    inArr = [NrFloor_SHP_noZero]
    for i, array in enumerate(inArr):
        newStat(X_floors_shp, Y_floors_shp, array, 0, outRasterPath+'Average_NrFloors_noZero_SHP.tif')
     
    inArr = [NrFloor_Access_noZero]
    for i, array in enumerate(inArr):
        newStat(X_floors_Access, Y_floors_Access, array, 0, outRasterPath+'Average_NrFloors_noZero_Access.tif')
    
    
    


    
if __name__ == "__main__":
    start = time.time()
    inputCSV = "/home/simulant/ag_lukas/personen/Mostafa/Frankfurt Buildingblocks/RasterInputs.csv"
    outRasterPath = "/home/simulant/ag_lukas/personen/Mostafa/Frankfurt Buildingblocks/Raster/"
    zonStat_selectedArea(inputCSV, outRasterPath)
    print(time.time() - start)