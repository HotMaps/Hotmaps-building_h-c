import gdal, os
import numpy as np


import CM_intern.common_modules.array2raster as a2r
'''
This code is performed for raster layers which their extent is greater than the base raster. 
also their resolution should be smaller or equal to the base raster and also be a multiplicand of "10".

Here also it should be noted that the input raster should have the dimensions of bigger than the cut raster. otherwise, the output is not correct.
'''


def RastExtMod(TobeClippedRasterPath, baseRasterPath, dataType, outRasterPath
               , noDataValue, saveAsRaster= True):
    
    """
    ########################################
    # Load Raster layer file
    # Cut with boundaries fminx,..fmaxy
    # Return cutted Raster layer image
    ######################################
    cutRastDatasource = gdal.Open(InputRasterFile)
    transform = cutRastDatasource.GetGeoTransform()
    minx = transform[0]
    maxy = transform[3]

    
    # define exact index that encompasses the feature.
    lowIndexY=max(0, int((fminx-minx)/1000.0))
    lowIndexX=max(0, int((maxy-fmaxy)/1000.0))
    upIndexY=lowIndexY+int((fmaxx-fminx)/1000.0)
    upIndexX=lowIndexX+int((fmaxy-fminy)/1000.0)
    while minx + upIndexY*1000 < fmaxx:
        upIndexY = upIndexY + 1
    while maxy - upIndexX*1000 > fminy:
        upIndexX = upIndexX + 1
        
    
    # considering the 1km resolution of strd raster, the raster origin should be a factor of 1000. this will be done in the following code.
    rasterOrigin2 = (minx + lowIndexY*1000,maxy - lowIndexX*1000)
    b11 = cutRastDatasource.GetRasterBand(1)
    arr1 = b11.ReadAsArray()
    arr_out= arr1[lowIndexX:upIndexX,lowIndexY:upIndexY]

    return (OutputRasterFile, rasterOrigin2, 1000, -1000
            , datatype, arr_out , 0)
    
    
    
    """
    
    
    
    
    
    baseRastDatasource = gdal.Open(baseRasterPath)
    transform = baseRastDatasource.GetGeoTransform()
    baseminx = transform[0]
    basemaxy = transform[3]
    #maxx = minx + transform[1] * cutRastDatasource.RasterXSize
    #miny = maxy + transform[5] * cutRastDatasource.RasterYSize
    rasterOrigin = (baseminx, basemaxy)
    b = baseRastDatasource.GetRasterBand(1)
    arr = b.ReadAsArray()
    x_res = arr.shape[0] 
    y_res = arr.shape[1]      
    del baseRastDatasource, arr
    
    TobeClippedRastDatasource = gdal.Open(TobeClippedRasterPath)
    transform2 = TobeClippedRastDatasource.GetGeoTransform()
    baseminX = transform2[0]
    basemaxY = transform2[3]
    #maxX = minX + transform2[1] * inRastDatasource.RasterXSize
    #minY = maxY + transform2[5] * inRastDatasource.RasterYSize
       
    x_res_factor = abs(transform[1]/transform2[1])
    y_res_factor = abs(transform[5]/transform2[5])
    x_dim = int(x_res * x_res_factor)
    y_dim = int(y_res * y_res_factor)
    
    arr_out = np.zeros((x_dim, y_dim),dtype = dataType)
    pixelWidth = transform2[1]
    pixelHeight = transform2[5]
    b2 = TobeClippedRastDatasource.GetRasterBand(1)
    arr2 = b2.ReadAsArray()

    xoff = int(abs((basemaxY - basemaxy)/transform2[5]))
    yoff = int(abs((baseminx - baseminX)/transform2[1]))

    arr_out[:,:] = arr2[xoff:xoff+x_dim, yoff:yoff+y_dim]

    del TobeClippedRastDatasource, arr2

    if saveAsRaster:
        # export array as raster file to disk
        a2r.array2rasterfile(outRasterPath, rasterOrigin, pixelWidth
                         , pixelHeight, dataType
                         , arr_out, noDataValue) 
        
    return (outRasterPath, rasterOrigin, pixelWidth
                         , pixelHeight, dataType
                         , arr_out, noDataValue)
    
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