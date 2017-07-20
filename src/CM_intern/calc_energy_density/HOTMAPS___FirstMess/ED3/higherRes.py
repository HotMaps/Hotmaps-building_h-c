import gdal, ogr, os, osr, time
import numpy as np
#import array2raster as a2r
from cython_files.SumOfHighRes_64 import CalcHighRes
#from cython_files.SumOfHighRes_py import CalcHighRes
'''
This code consideres the input raster with resolution of 1km2 and outputs a raster with 100m2 resolution. in case, different configuration in term of resolution
is required, the corresponding factors should be set again (x_res_factor and y_res_factor)

pixelWidth and pixelHeight are used for the output raster file.
'''

def HighRes(inRasterPath, pixelWidth, pixelHeight, dataType, outRasterPath, noDataValue, rasterOrigin = None):
    
    if rasterOrigin != None and type(inRasterPath).__name__ == "ndarray" :
        arr = inRasterPath
     
    else:   
        inDatasource = gdal.Open(inRasterPath)
        gt = inDatasource.GetGeoTransform()
        minx = gt[0]
        maxy = gt[3]
        rasterOrigin = (minx,maxy)
        b = inDatasource.GetRasterBand(1)
        arr = b.ReadAsArray()

    #maxx = minx + gt[1] * inDatasource.RasterXSize
    #miny = maxy + gt[5] * inDatasource.RasterYSize
    
    #x_res = arr.shape[0]
    #y_res = arr.shape[1]
    #x_res_factor = 10
    #y_res_factor = 10
    #x_dim = int(x_res * x_res_factor)
    #y_dim = int(y_res * y_res_factor)

    """
    st =time.time()
    arr_out = np.zeros((x_dim,y_dim),dtype = dataType)
    for i in range(x_res):
        for j in range(y_res):
            for m in range(x_res_factor):
                for n in range(y_res_factor):
                    arr_out[x_res_factor*i+m , y_res_factor*j+n] = arr[i,j]
    print (time.time() - st)
    
    print (np.sum(arr_out != arr_out1))
    raise
    """
    
    """
    # st =time.time()
    # Vectorisiert um den Factor 60+ schneller
    st = time.time()
    idxM_x_res = ((np.floor(np.arange(x_dim) / x_res_factor))[:, np.newaxis] * np.ones(y_dim)).astype("uint32")
    idxM_y_res = (np.ones((x_dim, 1)) *  np.floor(np.arange(y_dim) / y_res_factor)).astype("uint32")
    arr_out = arr[idxM_x_res, idxM_y_res] 
    print (time.time()-st) 
    """ 
    #st = time.time() 
    #Cython file nochmals schneller
    arr_out = CalcHighRes(arr, 10)
    #print (time.time()-st)
    
     
      
    
    
 
    return (outRasterPath, rasterOrigin, pixelWidth, pixelHeight, dataType, arr_out , noDataValue)

    
if __name__ == "__main__":
    start_time = time.time()
    prj_path = "/home/simulant/ag_lukas/personen/Mostafa/EnergyDensityII"
    temp_path            = prj_path  + os.sep + "Temp"
    data_path            = prj_path  + os.sep + "Data"
    noDataValue = 0
    outRasterPath = prj_path+os.sep+"Pop_1km_100m.tif"
    pixelHeight=100
    pixelWidth=100
    inRasterPath= data_path + os.sep + "Population.tif"
    dataType = "float32"
    HighRes(inRasterPath, pixelWidth, pixelHeight, dataType, outRasterPath, noDataValue)
    elapsed_time = time.time() - start_time
    print(elapsed_time)