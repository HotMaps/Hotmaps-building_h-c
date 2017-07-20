from osgeo import gdal, ogr, os, osr, time
import os, math
import numpy as np


def array2raster(newRasterfn,rasterOrigin,pixelWidth,pixelHeight,datatype,array,NoData_value):
    # conversion of data types from numpy to gdal
    dict ={"int8" : gdal.GDT_Byte, "int16" : gdal.GDT_Int16, "int32" : gdal.GDT_Int32, "uint16" : gdal.GDT_UInt16, "uint32" : gdal.GDT_UInt32, "float32" : gdal.GDT_Float32, "float64" : gdal.GDT_Float64}
    cols = array.shape[1]
    rows = array.shape[0]
    originX = rasterOrigin[0]
    originY = rasterOrigin[1]
    
    driver = gdal.GetDriverByName('GTiff')
    outRaster = driver.Create(newRasterfn, cols, rows, 1, dict[datatype], ['compress=LZW'])
    outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
    outband = outRaster.GetRasterBand(1)
    outband.SetNoDataValue(NoData_value)
    outband.WriteArray(array)
    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromEPSG(3035)
    outRaster.SetProjection(outRasterSRS.ExportToWkt())
    outband.FlushCache()


def cut2array(in_rast_path, cut_raster_path, datatype, out_raster_path,NoData_value):
    cutRastDatasource = gdal.Open(cut_raster_path)
    transform = cutRastDatasource.GetGeoTransform()
    #rasterOrigin = (transform[0], transform[3])
    rasterOrigin = (944000, 942000)
    #print(rasterOrigin)
    
    b = cutRastDatasource.GetRasterBand(1)
    arr = b.ReadAsArray()
    x_res = arr.shape[0]     # 4472
    y_res = arr.shape[1]     # 5559   
    cutRastDatasource = None
    arr_out = np.zeros((x_res*10, y_res*10),dtype = datatype)
    
    inRastDatasource = gdal.Open(in_rast_path)
    b = inRastDatasource.GetRasterBand(1)
    arr = b.ReadAsArray()
    
    xoff = 20
    yoff = 1
    
    for i in range(x_res*10):
        for j in range(y_res*10):
            arr_out[i,j] = arr[i+xoff, j+yoff]
    inRastDatasource = None
    rev_arr = arr_out[::-1]
    arr = None
    
    
    # rev_array = arr_out[::-1] # reverse array so the tif looks like the array
    # arr_out = None
    array2raster(out_raster_path, rasterOrigin, 100, 100, datatype, rev_arr, NoData_value) # convert array to raster
    


    

if __name__ == "__main__":
    start_time = time.time()
    
    prj_path = "/home/simulant/ag_lukas/personen/Mostafa/EnergyDensityII"
    temp_path            = prj_path  + os.sep + "Temp"
    data_path            = prj_path  + os.sep + "Data"
    datatype = "float32"
    rasterOrigin = (944000, 942000)
    NoData_value = 0
    '''
    in_rast_path = temp_path + os.sep + "temp1.tif"
    cut_raster_path = data_path + os.sep + "Population.tif"
    out_raster_path = prj_path + os.sep + "ss_pop_cut.tif"
    
    
    cut2array(in_rast_path, cut_raster_path, datatype, out_raster_path,NoData_value)
    '''
    r1 = prj_path + os.sep + "ss_pop_cut.tif"
    r2 = prj_path + os.sep + "Pop_1km_100m.tif"
    r3 = prj_path + os.sep + "sum_ss_1km.tif"
    r4 = prj_path + os.sep + "Dem_in_Nuts.tif"
    r5 = prj_path + os.sep + "Pop_in_Nuts.tif"
    #output = prj_path + os.sep + "demand_v2.tif" 
    output = prj_path + os.sep + "test11.tif" 
    # Open band one of the raster layers
    # ds1: ss(100m2); ds2: population(1km2); ds3: sum(ds1) in 1km2; ds4: demand in nuts3; ds5: population in nuts3
    '''
    ds1 = gdal.Open(r1)
    b11 = ds1.GetRasterBand(1)
    arr1 = b11.ReadAsArray()
    
    ds2 = gdal.Open(r2)
    b21 = ds2.GetRasterBand(1)
    arr2 = b21.ReadAsArray()
    '''

    ds3 = gdal.Open(r3)
    b31 = ds3.GetRasterBand(1)
    arr3 = b31.ReadAsArray()
    x=b31.GetNoDataValue()
    xres=arr3.shape[0]
    yres=arr3.shape[1]
    for i in range(xres):
        for j in range(yres):
            if arr3[i,j] != x:
                if math.isnan(arr3[i,j]):
                    print("(%s ,%s)" %(i,j))
                
    
    
    
    '''
    ds4 = gdal.Open(r4)
    b41 = ds4.GetRasterBand(1)
    arr4 = b41.ReadAsArray()
    
    ds5 = gdal.Open(r5)
    b51 = ds5.GetRasterBand(1)
    arr5 = b51.ReadAsArray()
    '''
    # apply equation
    # data = (arr3>0)*arr1*arr2*arr4/arr3/arr5 + (arr3==0)*arr2*arr4/arr5/100.0
    # data = (arr3>0)*(arr5==0)
    # print(b31.GetNoDataValue())
    
    #print('min: %s, max: %s, mean: %s, std: %s' %(arr3.min(), arr3.max(), arr3.mean(), arr3.std()))
    
    ds1 = None
    ds2 = None
    ds3 = None
    ds4 = None
    ds5 = None
    
    #array2raster(output, rasterOrigin, 100, 100, datatype, data,NoData_value) # convert array to raster


    
    

    elapsed_time = time.time() - start_time
    print(elapsed_time)
    