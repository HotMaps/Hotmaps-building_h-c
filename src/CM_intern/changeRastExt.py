import os
import math
import time
import numpy as np
from osgeo import gdal
from array2raster import array2raster

'''
This code is performed for raster layers which their extent is greater than population raster. 
also their resolution should be smaller or equal to the population raster and also be a multiplicand of "10".

Here also it should be noted that the input raster should have the dimensions of bigger than the cut raster. otherwise, the output is not correct.
'''


def RastExtMod(inRasterPath, cutRasterPath, dataType, outRasterPath,noDataValue, saveAsRaster= True):
    cutRastDatasource = gdal.Open(cutRasterPath)
    transform = cutRastDatasource.GetGeoTransform()
    minx = transform[0]
    maxy = transform[3]
    maxx = minx + transform[1] * cutRastDatasource.RasterXSize
    miny = maxy + transform[5] * cutRastDatasource.RasterYSize
    rasterOrigin = (minx, maxy)
    b = cutRastDatasource.GetRasterBand(1)
    arr = b.ReadAsArray()
    inRastDatasource = gdal.Open(inRasterPath)
    transform2 = inRastDatasource.GetGeoTransform()
    minX = transform2[0]
    maxY = transform2[3]
    maxX = minX + transform2[1] * inRastDatasource.RasterXSize
    minY = maxY + transform2[5] * inRastDatasource.RasterYSize
    x_res = arr.shape[0]     # 4472
    x_res_factor = abs(transform[1]/transform2[1])
    y_res = arr.shape[1]     # 5559
    y_res_factor = abs(transform[5]/transform2[5])
    x_dim = int(x_res * x_res_factor)
    y_dim = int(y_res * y_res_factor)
    cutRastDatasource = None
    arr_out = np.zeros((x_dim, y_dim),dtype = dataType)
    pixelWidth = transform2[1]
    pixelHeight = transform2[5]
    b2 = inRastDatasource.GetRasterBand(1)
    arr2 = b2.ReadAsArray()

    xoff = abs((maxY - maxy)/transform2[5])
    yoff = abs((minx - minX)/transform2[1])
    """
    # 5 sec versus 0.0001 sec fpr AT130/AT222/AT127
    for i in range(x_dim):
        for j in range(y_dim):
            arr_out[i,j] = arr2[i+xoff, j+yoff]
    """
    arr_out[:,:] = arr2[xoff:xoff+x_dim, yoff:yoff+y_dim]
    arr = None
    inRastDatasource = None

    if saveAsRaster:
        array2raster(outRasterPath, rasterOrigin, pixelWidth, pixelHeight, dataType, arr_out, noDataValue) # convert array to raster
        arr = None
    else: 
        return arr_out
    
    
if __name__ == "__main__":

    prj_path = "/home/simulant/ag_lukas/personen/Mostafa/EnergyDensityII"
    temp_path            = prj_path  + os.sep + "Temp"
    data_path            = prj_path  + os.sep + "Data"
    dataType = "int16"
    noDataValue = 0

    inRasterPath = temp_path + os.sep + "temp1.tif"
    cutRasterPath = data_path + os.sep + "Population.tif"
    outRasterPath = prj_path + os.sep + "test1.tif"
    
    
    
    RastExtMod(inRasterPath, cutRasterPath, dataType, outRasterPath,noDataValue)