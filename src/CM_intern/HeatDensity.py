import numpy as np
import shutil
import sys, os, time, gdal, ogr
from array2raster import array2raster
from changeRastExt import RastExtMod
from higherRes import HighRes
from query import query
from rasterize import rasterize
#from zonal_statistics import ZonalStat


linux = "linux" in sys.platform

# Weigthing maxtric for heat demand based on Corine Land Cover information
CORINE_LANDCOVER_TRANSFORM_MATRIX = np.zeros(500,dtype="f8") + 0.015
CORINE_LANDCOVER_TRANSFORM_MATRIX[1] = 1 # Continuous urban fabric
CORINE_LANDCOVER_TRANSFORM_MATRIX[2] = 0.9 # Discontinuous urban fabric

CORINE_LANDCOVER_TRANSFORM_MATRIX[3] = 0.7 # Industrial or commercial units
CORINE_LANDCOVER_TRANSFORM_MATRIX[10] = 0.1 # Green urban areas
CORINE_LANDCOVER_TRANSFORM_MATRIX[11] = 0.1 # Sport and leisure facilities
CORINE_LANDCOVER_TRANSFORM_MATRIX[18] = 0.5 # Pastures
CORINE_LANDCOVER_TRANSFORM_MATRIX[20] = 0.5 # Complex cultivation patterns
CORINE_LANDCOVER_TRANSFORM_MATRIX[21] = 0.5 # Land principally occupied by agriculture
#CORINE_LANDCOVER_TRANSFORM_MATRIX[4] = 0.1 # Road and rail networks and associated land
#CORINE_LANDCOVER_TRANSFORM_MATRIX[6] = 0.1 # Airports

#CORINE_LANDCOVER_TRANSFORM_MATRIX[:] = 1
def HeatDensity(r1, r2, r3, r4, r5, r7, rasterOrigin, output):
    eps = np.finfo(float).eps
    ds1 = gdal.Open(r1)
    b11 = ds1.GetRasterBand(1)
    arr1 = b11.ReadAsArray().astype("f4") 
    
    ds2 = gdal.Open(r2)
    b21 = ds2.GetRasterBand(1)
    arr2 = b21.ReadAsArray().astype("f4") 
        
    ds3 = gdal.Open(r3)
    b31 = ds3.GetRasterBand(1)
    arr3 = b31.ReadAsArray().astype("f4")         
        
    ds4 = gdal.Open(r4)
    b41 = ds4.GetRasterBand(1)
    arr4 = b41.ReadAsArray().astype("f4") 
    
    ds5 = gdal.Open(r5)
    b51 = ds5.GetRasterBand(1)
    arr5 = b51.ReadAsArray().astype("f4")  
    
    ds7 = gdal.Open(r7)
    b71 = ds7.GetRasterBand(1)
    arr7 = b71.ReadAsArray().astype("f4")   
        
       
    ds1 = None
    ds2 = None
    ds3 = None
    ds4 = None
    ds5 = None    
    noDataValue = 0
    pixelWidth = 100
    pixelHeight = -100
    datatype = 'float32'
    
    result = (arr5>0)*((arr3>0)*arr1*arr2*arr4*(arr7/100)/(arr3+eps)/(arr5+eps) + (arr3==0)*arr2*arr4/(arr5+eps)/100.0)
    array2raster(output, rasterOrigin, pixelWidth, pixelHeight, datatype, result, noDataValue)
    print(output)
    result = (arr5>0)*((arr3>0)*arr1*arr2*arr4/(arr3+eps)/(arr5+eps) + (arr3==0)*arr2*arr4/(arr5+eps)/100.0)
    array2raster(output + "_no_CLC", rasterOrigin, pixelWidth, pixelHeight, datatype, result, noDataValue)
    print(output + "_no_CLC")
    result = None


#@profile
def main_process():

    start_time = time.time()
    
    if linux:
        prj_path    = "/home/simulant/ag_lukas/personen/Mostafa/HeatDensityMap - Copy"
        prj_path_output    = "output"    
    else:
        prj_path    = "Z:/personen/Mostafa/HeatDensityMap - Copy"
    
    org_data_path    = prj_path  + os.sep + "Original Data"
    proc_data_path    = prj_path  + os.sep + "Processed Data"    
    temp_path        = prj_path  + os.sep + "Temp"
    
    # inputs
    strd_vector_path = org_data_path+ os.sep + "NUTS3.shp"
    strd_raster_path_full = org_data_path+ os.sep + "Population.tif"
    strd_raster_path = "%s_small.tif" % strd_raster_path_full[:-4]
    #strd_raster_path = strd_raster_path_full
    # outputs
    #r1                = prj_path_output + os.sep + "ss_pop_cut.tif"
    r1                = proc_data_path + os.sep + "ss_pop_cut.tif"
    r2                = proc_data_path + os.sep + "Pop_1km_100m.tif"
    r3                = proc_data_path + os.sep + "sum_ss_1km.tif"
    #r4                = proc_data_path + os.sep + "Dem_in_Nuts.tif"
    r4                = temp_path + os.sep + "temp4.tif"
    r5                = proc_data_path + os.sep + "Pop_in_Nuts.tif"
    r6                = proc_data_path + os.sep + "CorineLU.tif"
    r7                = proc_data_path + os.sep + "CorineLU_cut.tif"
    
    output            = proc_data_path + os.sep + "demand_v2.tif" 
    
    # array2raster output datatype
    datatype = 'int32'
    
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
    """if os.path.exists(r1):
        process1 = False
    if os.path.exists(r2):
        process2 = False
    if os.path.exists(r3):
        process3 = False
    if os.path.exists(r4):
        process4 = False
    if os.path.exists(r5):
        process5 = False
    """
    
    # common parameters
    noDataValue = -17.3
    #Standard population raster layer
    # cut standard population raster
    """
    """
    if strd_raster_path_full != strd_raster_path and process1 == True:
        key_field = "NUTS_ID"
        feat_id_LIST = [14,15,13]  # 14refers to the feature ID of Vienna
        #feat_id_LIST = [14]  # 14refers to the feature ID of Vienna
        feat_id_LIST = range(1290,1300)  # 14refers to the feature ID of Vienna
        # Load NUTS3 Layer select specific feature (certain Nuts3 region)
        inDriver = ogr.GetDriverByName("ESRI Shapefile")
        inDataSource = inDriver.Open(strd_vector_path, 0)
        inLayer = inDataSource.GetLayer()
        fminx = fminy = 10**10
        fmaxx = fmaxy = 0
        for feat_id in feat_id_LIST:
            inFeature = inLayer.GetFeature(feat_id)
            print (inFeature.GetField(key_field))
            geom = inFeature.GetGeometryRef()
            #Get boundaries
            fminx_, fmaxx_, fminy_, fmaxy_ = geom.GetEnvelope()
            fminx = min(fminx_, fminx)
            fminy = min(fminy_, fminy)
            fmaxx = max(fmaxx_, fmaxx)
            fmaxy = max(fmaxy_, fmaxy)        
        
        ########################################
        # Load population layer
        # Cut with boundaries defined by Shape of NUSTS 3 Layer
        # Save smaller population layer image
        ######################################
        cutRastDatasource = gdal.Open(strd_raster_path_full)
        transform = cutRastDatasource.GetGeoTransform()
        minx = transform[0]
        maxy = transform[3]
        maxx = minx + transform[1] * cutRastDatasource.RasterXSize
        miny = maxy + transform[5] * cutRastDatasource.RasterYSize
        rasterOrigin = (minx, maxy)
        
        # define exact index that encompasses the feature.
        lowIndexY=int((fminx-minx)/1000.0)
        lowIndexX=int((maxy-fmaxy)/1000.0)
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
        array2raster(strd_raster_path, rasterOrigin2, 1000, -1000, datatype,arr_out , 0)
        cutRastDatasource = None
        arr1 = None
        arr_out = None
        ########################################
        # END
        #
        ######################################
    
    #Load (smaller) population layer         
    cutRastDatasource = gdal.Open(strd_raster_path)


    transform = cutRastDatasource.GetGeoTransform()
    minx = transform[0]
    maxy = transform[3]
    maxx = minx + transform[1] * cutRastDatasource.RasterXSize
    miny = maxy + transform[5] * cutRastDatasource.RasterYSize
    extent = (minx,maxx,miny,maxy)
    rasterOrigin = (minx, maxy)
    
    #print(extent)
    #raise

    cutRastDatasource = None


    if process1:
        # cuts SOIL Sealing cuts to same size as population layer, smaller data processing (Values above 100%...)
        # Save as raster layer
        st = time.time()
        print("Process 1")
        in_rast_path = org_data_path + os.sep + "SS2012.tif"
        datatype='int16'
        out_raster_path = temp_path + os.sep + "temp1.tif"
        pixelWidth = 100
        pixelHeight = -100
        RastExtMod(in_rast_path, strd_raster_path, datatype, out_raster_path, noDataValue)
     
        ds1 = gdal.Open(out_raster_path)
        b11 = ds1.GetRasterBand(1)
        arr1 = b11.ReadAsArray()
        data = np.zeros_like(arr1)
        idxM = arr1 > 0
        data[idxM] = arr1[idxM]
        data = np.minimum(100, data)
        #data = (arr1<101)*arr1
        array2raster(r1, rasterOrigin, pixelWidth, pixelHeight, datatype, data, noDataValue)
        data = None
        ds1 = None
        elapsed_time = time.time() - st
        print (r1)
        print("Process 1 took: %s seconds" %elapsed_time)
    
    if process1:      
        # cuts Corine cuts to same size as population layer, smaller data processing (Values above 100%...)
        # Save as raster layer
        st = time.time()
        print("Process 1a Corine Landcover data")
        in_rast_path = org_data_path + os.sep + "g100_clc12_V18_5.tif"
        datatype='int16'
        out_raster_path = r7
        pixelWidth = 100
        pixelHeight = -100
        RastExtMod(in_rast_path, strd_raster_path, datatype, out_raster_path, noDataValue)
     
        ds1 = gdal.Open(out_raster_path)
        b11 = ds1.GetRasterBand(1)
        arr1 = b11.ReadAsArray()
        
        data_CLC = (CORINE_LANDCOVER_TRANSFORM_MATRIX[arr1] * 100).astype(datatype)
        
        array2raster(r7, rasterOrigin, pixelWidth, pixelHeight, datatype, data_CLC, noDataValue)

        ds1 = None
        elapsed_time = time.time() - st
        print (r7)
        print("Process 1a took: %s seconds" %elapsed_time)
        
    if process2:
        # transforms population layer from 1x1 km to 100x100m
        # saves as raster layer
        st = time.time()
        print("Process 2")
        in_raster_path = strd_raster_path
        pixelWidth = 100
        pixelHeight = -100
        datatype = 'float32'
        HighRes(in_raster_path, pixelWidth, pixelHeight, datatype, r2, noDataValue)
        elapsed_time = time.time() - st
        print (r1)
        print("Process 2 took: %s seconds" %elapsed_time)

    
        
    if process3:
        # Calculate sum of soilsailing (100x100 m) for 1x1 km and write that sum on the 100x100 m layer
        # save new raster layer
        st = time.time()
        print("Process 3")
        input_value_raster = r1
        dataType = 'float32'
        outRasterPath = temp_path + os.sep + "temp2.tif"
        pixelWidth = 100
        pixelHeight = -100
        ds1 = gdal.Open(input_value_raster)
        b11 = ds1.GetRasterBand(1)
        arr1 = b11.ReadAsArray()
        #Consider Corine Landcover Data
        array2raster(r3 + "dummy_before",rasterOrigin,pixelWidth,pixelHeight,dataType,arr1,noDataValue)
        arr1 *= data_CLC / 100.0
        array2raster(r3 + "dummy_after",rasterOrigin,pixelWidth,pixelHeight,dataType,arr1,noDataValue)
        row = arr1.shape[0]
        col = arr1.shape[1]
        row1 = int(row/10)
        col1 = int(col/10)
        temp = 0
        arr_out = np.zeros((row, col),dtype = dataType)
        arr_out2= np.zeros((row, col),dtype = dataType)
        arr_1_km = np.zeros((row1, col1), dtype="uint16")
        arr_1100 = np.zeros((row1, col), dtype="uint16")


        idx_m_base = np.arange(row1) *10 
        idx_n_base = np.arange(col1) *10 
        """
        for m in range(10):
            idx_m = idx_m_base + m
            
            for n in range(10):
                idx_n = idx_n_base + n
                arr_1_km += arr1[idx_m,:][:, idx_n]
                #temp = temp + arr1[10*i+m,10*j+n]
        print( "------")
        print (arr_1_km);print( "------")
        print (np.sum(arr_1_km))
        arr_1_km = np.zeros((row1, col1), dtype="uint16")    
        """
        for m in range(10):
            idx_m = idx_m_base + m
            arr_1100[:,:] += arr1[idx_m,:]
        for n in range(10):
            idx_n = idx_n_base + n
            arr_1_km += arr_1100[:, idx_n]
        #print (arr_1_km);print( "------")
        #print (np.sum(arr_1_km));print( "------")
        #temp = temp + arr1[10*i+m,10
        idx_m_100 = np.reshape(np.ones((10,1),dtype="uint16") * idx_m_base / 10, idx_m_base.shape[0] * 10, 1)
        idx_n_100 = np.reshape(np.ones((10,1),dtype="uint16") * idx_n_base / 10, idx_n_base.shape[0] * 10, 1)
        arr_out[:, :] = arr_1_km[idx_m_100, :][:, idx_n_100]              

        
        
        
        '''
        for i in range(row1):
            for j in range(col1):
                
                for m in range(10):
                    for n in range(10):
                        temp = temp + arr1[10*i+m,10*j+n]
                for m in range(10):
                    for n in range(10):
                        arr_out2[10*i+m,10*j+n] = temp
                temp = 0
        print (time.time() -st)
        '''

        ds1 = None
        arr1 = None
        array2raster(r3,rasterOrigin,pixelWidth,pixelHeight,dataType,arr_out,noDataValue)
        elapsed_time3 = time.time() - st
        print (r3)
        print("Process 3 took: %s seconds" %elapsed_time3)
    
    if process4:
        # takes vector layer (vectors are squares (1x1km - same size as population raster layer))
        # Information stored in Pop_Nuts.shape: NUmber of population per 1km and corresponding NUTS3 region
        # and Energy Demand per Nuts region (vector layer)
        # Store Energy Demand of corresponding NUTS REGION to each 1x1km feature
        st = time.time()
        print("Process 4")
        input_vec_path = proc_data_path + os.sep + "Pop_Nuts.shp"
        dict_lyr_path = proc_data_path + os.sep +"NUTS_Demand.shp"
        key_field = "NUTS_ID"
        value_field = "ESPON_TOTA"
        out_field_name = "NutsDem"
        output_lyr_path =  temp_path + os.sep + "temp3.shp"
        inVectorPath = output_lyr_path
        fieldName = "NutsDem"
        dataType = 'float32'
        st1 = time.time()
        query(input_vec_path, extent, dict_lyr_path, key_field, value_field, out_field_name, output_lyr_path)
        rasterize(strd_raster_path, inVectorPath, fieldName, dataType, r4, noDataValue)
        elapsed_time = time.time() - st
        print("Process 4 took: %s seconds" %elapsed_time)
       
    if process5:
        # takes vector layer (vectors are squares (1x1km - same size as population raster layer))
        # Information stored in Pop_Nuts.shape: NUmber of population per 1km and corresponding NUTS3 region
        # and Population per Nuts region (vector layer), same as the one two lines above
        # Population of corresponding NUTS 3 REGION to each 1x1km feature 
        st = time.time()
        print("Process 5")
        input_vec_path = proc_data_path + os.sep + "Pop_Nuts.shp"
        dict_lyr_path = proc_data_path + os.sep +"Pop_Nuts.shp"
        key_field = "NUTS_ID"
        value_field =  "GEOSTAT_gr"
        out_field_name = "NutsPop"
        output_lyr_path =  temp_path + os.sep + "temp5.shp"
        inVectorPath = output_lyr_path
        fieldName = "NutsPop"
        dataType = 'uint32'
        query(input_vec_path, extent, dict_lyr_path, key_field, value_field, out_field_name, output_lyr_path)    
        rasterize(strd_raster_path, inVectorPath, fieldName, dataType, r5, noDataValue)
        elapsed_time = time.time() - st
        print("Process 5 took: %s seconds" %elapsed_time)

    
                
    print ("Outputfile: %s" % output)
    HeatDensity(r1, r2, r3, r4, r5, r7, rasterOrigin, output)
    
    elapsed_time = time.time() - start_time
    print("The whole process took: %s seconds" %elapsed_time)

    # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX Close XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    if del_temp_path:
        if os.path.exists(temp_path):
            shutil.rmtree(temp_path)
    sys.exit("Done!")

    
if __name__ == "__main__":
    
    main_process()