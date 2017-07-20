import sys, os, time, gdal
from array2raster import array2raster
from rasterize import rasterize
from zonal_statistics import ZonalStat
from query import query
from changeRastExt import RastExtMod
from higherRes import HighRes


linux = "linux" in sys.platform



def HeatDensity(r1, r2, r3, r4, r5, rasterOrigin, output):

    ds1 = gdal.Open(r1)
    b11 = ds1.GetRasterBand(1)
    arr1 = b11.ReadAsArray()
    
    ds2 = gdal.Open(r2)
    b21 = ds2.GetRasterBand(1)
    arr2 = b21.ReadAsArray()
        
    ds3 = gdal.Open(r3)
    b31 = ds3.GetRasterBand(1)
    arr3 = b31.ReadAsArray()        
        
    ds4 = gdal.Open(r4)
    b41 = ds4.GetRasterBand(1)
    arr4 = b41.ReadAsArray()
    
    ds5 = gdal.Open(r5)
    b51 = ds5.GetRasterBand(1)
    arr5 = b51.ReadAsArray()    
        
    result = (arr5>0)*((arr3>0)*arr1*arr2*arr4/arr3/arr5 + (arr3==0)*arr2*arr4/arr5/100.0)
    
    ds1 = None
    ds2 = None
    ds3 = None
    ds4 = None
    ds5 = None    
    noDataValue = 0
    pixelWidth = 100
    pixelHeight = 100
    datatype = 'float32'
    array2raster(output, rasterOrigin, pixelWidth, pixelHeight, datatype, result, noDataValue)
    result = None



if __name__ == "__main__":

    start_time = time.time()
    elapsed_time = time.time()
    if linux:
        prj_path    = "/home/simulant/ag_lukas/personen/Mostafa/HeatDensityMap - Copy"
    else:
        prj_path    = "Z:/personen/Mostafa/HeatDensityMap - Copy"
    
    org_data_path    = prj_path  + os.sep + "Original Data"
    proc_data_path    = prj_path  + os.sep + "Processed Data"    
    temp_path        = prj_path  + os.sep + "Temp"
    
    # inputs
    strd_raster_path = org_data_path+ os.sep + "Population.tif"
    
    # outputs
    r1                = proc_data_path + os.sep + "ss_pop_cut.tif"
    r2                = proc_data_path + os.sep + "Pop_1km_100m.tif"
    r3                = proc_data_path + os.sep + "sum_ss_1km.tif"
    #r4                = proc_data_path + os.sep + "Dem_in_Nuts.tif"
    r4                = temp_path + os.sep + "temp4.tif"
    r5                = proc_data_path + os.sep + "Pop_in_Nuts.tif"
    output            = proc_data_path + os.sep + "demand_v2.tif" 
    

    
    del_temp_path    = False
    process1           = True
    process2           = True
    process3           = True
    process4         = True
    process5        = True

    
    if del_temp_path:    
        if os.path.exists(temp_path):
            shutil.rmtree(temp_path)   
        if not os.path.exists(temp_path):
            os.makedirs(temp_path)    
    if os.path.exists(r1):
        process1 = False
    if os.path.exists(r2):
        process2 = False
    if os.path.exists(r3):
        process3 = False
    if os.path.exists(r4):
        process4 = False
    if os.path.exists(r5):
        process5 = False

    # common parameters
    noDataValue = 0
    cutRastDatasource = gdal.Open(strd_raster_path)
    transform = cutRastDatasource.GetGeoTransform()
    minx = transform[0]
    maxy = transform[3]
    maxx = minx + transform[1] * cutRastDatasource.RasterXSize
    miny = maxy + transform[5] * cutRastDatasource.RasterYSize
    rasterOrigin = (minx, miny)
    cutRastDatasource = None


        
    if process1:
    
        in_rast_path = org_data_path + os.sep + "SS2012.tif"
        datatype = 'uint8'
        out_raster_path = temp_path + os.sep + "temp1.tif"
        pixelWidth = 100
        pixelHeight = 100
        #RastExtMod(in_rast_path, strd_raster_path, datatype, out_raster_path, noDataValue)
        
        ds1 = gdal.Open(out_raster_path)
        b11 = ds1.GetRasterBand(1)
        arr1 = b11.ReadAsArray()
        data = (arr1<101)*arr1
        array2raster(r1, rasterOrigin, pixelWidth, pixelHeight, datatype, data, noDataValue)
        data = None
        ds1 = None
        elapsed_time = time.time() - start_time
        print("Process 1 took: %s seconds" %elapsed_time)
    
    if process2:
        in_raster_path = strd_raster_path
        pixelWidth = 100
        pixelHeight = 100
        datatype = 'float32'
        HighRes(in_raster_path, pixelWidth, pixelHeight, datatype, r2, noDataValue)
        elapsed_time = time.time() - elapsed_time
        print("Process 2 took: %s seconds" %elapsed_time)
    '''
    if process3:
        input_zone_polygon = org_data_path + os.sep + "Geostat_pop.shp"
        input_value_raster = r1
        jsonOutput = temp_path + os.sep + "temp2.geojson"
        output_path = temp_path + os.sep + "temp2.tif"
        pixelWidth = 100
        pixelHeight = 100
        datatype = 'uint16'
        ZonalStat(input_zone_polygon,input_value_raster, jsonOutput, output_path, ['sum'])
        HighRes(output_path, pixelWidth, pixelHeight, datatype, r3, noDataValue)
        elapsed_time = time.time() - elapsed_time
        print("Process 3 took: %s seconds" %elapsed_time)
    '''
    if process4:
        input_vec_path = proc_data_path + os.sep + "Pop_Nuts.shp"
        dict_lyr_path = proc_data_path + os.sep +"NUTS_Demand.shp"
        key_field = "NUTS_ID"
        value_field = "ESPON_TOTA"
        out_field_name = "NutsDem"
        output_lyr_path =  temp_path + os.sep + "temp3.shp"
        pixel_size = 100
        inVectorPath = output_lyr_path
        fieldName = "NutsDem"
        dataType = 'float32'
        # query(input_vec_path, dict_lyr_path, key_field, value_field, out_field_name, output_lyr_path)
        rasterize(strd_raster_path, inVectorPath, fieldName, dataType, r4, noDataValue)
        elapsed_time = time.time() - elapsed_time
        print("Process 4 took: %s seconds" %elapsed_time)
        
    if process5:
        input_vec_path = proc_data_path + os.sep + "Pop_Nuts.shp"
        dict_lyr_path = proc_data_path + os.sep +"Pop_Nuts.shp"
        key_field = "NUTS_ID"
        value_field =  "GEOSTAT_gr"
        out_field_name = "NutsPop"
        output_lyr_path =  temp_path + os.sep + "temp5.shp"
        pixel_size = 100
        inVectorPath = output_lyr_path
        fieldName = "NutsPop"
        dataType = 'uint32'
        # query(input_vec_path, dict_lyr_path, key_field, value_field, out_field_name, output_lyr_path)    
        rasterize(strd_raster_path, inVectorPath, fieldName, dataType, r5, noDataValue)

        elapsed_time = time.time() - elapsed_time
        print("Process 5 took: %s seconds" %elapsed_time)
    
    HeatDensity(r1, r2, r3, r4, r5, rasterOrigin, output)
    
    elapsed_time = time.time() - start_time
    print("The whole process took: %s seconds" %elapsed_time)

    # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX Close XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    if del_temp_path:
        if os.path.exists(temp_path):
            shutil.rmtree(temp_path)
    sys.exit("Done!")