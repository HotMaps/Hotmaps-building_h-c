import numpy as np
import shutil
import sys, os, time, gdal, ogr

import  modules.Subfunctions as SF
import  modules.array2raster as a2r
import  modules.changeRastExt as cre   # import RastExtMod
import  modules.higherRes as hr        # import HighRes
import  modules.query as qu
import  modules.rasterize as ra

#from zonal_statistics import ZonalStat

import modules.cython_files.SumOfHighRes_64 as SOHR
"""
try:
    from modules.cython_files.SumOfHighRes_64 import CalcSum as CoreLoopSumLowRes
    from modules.cython_files.SumOfHighRes_64 import CalcAverageBased
    from modules.cython_files.SumOfHighRes_64 import CalcHighRes
except:
    pass
    #from cython_files.SumOfHighRes import CalcSum as CoreLoopSumLowRes
    #from cython_files.SumOfHighRes import CalcAverageBased
#from cython_files.SumOfHighRes_py import CalcAverageBased
"""
DEBUG = False
linux = "linux" in sys.platform

# Weigthing maxtric for heat demand based on Corine Land Cover information
CORINE_LANDCOVER_TRANSFORM_MATRIX = np.zeros(500,dtype="f4") + 0.015
CORINE_LANDCOVER_TRANSFORM_MATRIX[1] = 1 # Continuous urban fabric
CORINE_LANDCOVER_TRANSFORM_MATRIX[2] = 0.9 # Discontinuous urban fabric

CORINE_LANDCOVER_TRANSFORM_MATRIX[3] = 0.7 # Industrial or commercial units
CORINE_LANDCOVER_TRANSFORM_MATRIX[10] = 0.1 # Green urban areas
CORINE_LANDCOVER_TRANSFORM_MATRIX[11] = 0.1 # Sport and leisure facilities
CORINE_LANDCOVER_TRANSFORM_MATRIX[18] = 0.5 # Pastures
CORINE_LANDCOVER_TRANSFORM_MATRIX[20] = 0.5 # Complex cultivation pattern
CORINE_LANDCOVER_TRANSFORM_MATRIX[21] = 0.5 # Land principally occupied by agriculture
#CORINE_LANDCOVER_TRANSFORM_MATRIX[4] = 0.1 # Road and rail networks and associated land
#CORINE_LANDCOVER_TRANSFORM_MATRIX[6] = 0.1 # Airports

#CORINE_LANDCOVER_TRANSFORM_MATRIX[:] = 1


  
EXPORT_LAYERS = True

#from memory_profiler import profile

#@profile
def HeatDensity(r1, r2, r3, r4, r5, r7, rasterOrigin, output):
    eps = np.finfo(float).eps
    
    noDataValue = 0
    pixelWidth = 100
    pixelHeight = -100
    datatype = 'float32'
    
    ##########################
    if type(r2).__name__ == "ndarray":
        arr2 = r2
    else:
        arr2 = SF.rrl(r2)
        """
        ds2 = gdal.Open(r2)
        b21 = ds2.GetRasterBand(1)
        arr2 = b21.ReadAsArray().astype("f4") 
        ds2 = None
        """
    result = np.zeros(arr2.shape, dtype="f4")   
    result[:, :] = arr2
    arr2 = None
    ##########################
    if type(r4).__name__ == "ndarray":
        arr4 = r4
    else:
        arr4 = SF.rrl(r4)
        """ds4 = gdal.Open(r4)
        b41 = ds4.GetRasterBand(1)
        arr4 = b41.ReadAsArray().astype("f4") 
        ds4 = None 
        """       
    result[:, :] *= arr4
    arr4 = None
    ##########################
    if type(r7).__name__ == "ndarray":
        arr7 = r7
    else:
        arr7 = SF.rrl(r7)
        """ds7 = gdal.Open(r7)
        b71 = ds7.GetRasterBand(1)
        arr7 = b71.ReadAsArray().astype("f4")   
        ds7 = None
        """
    result[:, :] *= arr7  
    arr7 = None
    ########################## 
    result /= 100.0
    
    ########################## 
    if type(r5).__name__ == "ndarray":
        arr5 = r5
    else:
        arr5 = SF.rrl(r5)
        """ds5 = gdal.Open(r5)
        b51 = ds5.GetRasterBand(1)
        arr5 = b51.ReadAsArray().astype("f4")  
        ds5 = None
        """
    result /= (arr5.astype("f4")+eps)
    arr5 = None
        
        
    ########################## 
    if type(r1).__name__ == "ndarray":
        arr1 = r1.astype("f4")
    else:
        arr1 = SF.rrl(r1)
        """ds1 = gdal.Open(r1)
        b11 = ds1.GetRasterBand(1)
        arr1 = b11.ReadAsArray().astype("f4") 
        ds1 = None 
        """   
    
    ##########################     
    if type(r3).__name__ == "ndarray":
        arr3 = r3.astype("f4")
    else:
        arr3 = SF.rrl(r3)
        """ds3 = gdal.Open(r3)
        b31 = ds3.GetRasterBand(1)
        arr3 = b31.ReadAsArray().astype("f4")         
        ds3 = None
        """
    arr3 += eps
    ########################## 
    idxM = (arr3 <= 2*eps)
    result[idxM] /= 100.0 
    
    
    idxM = (arr3 > 2*eps)
    result[idxM] *= (arr1/arr3)[idxM] 
    arr1 = None
    idxM = None
    arr3 = None
    #print np.sum(result)
    #print time.time() -st
    a2r.array2raster(output, rasterOrigin, pixelWidth, pixelHeight, datatype, result, noDataValue)
    print(output)
    
    """
    result = (arr5>0)*((arr3>0)*arr1*arr2*arr4/(arr3+eps)/(arr5+eps) + (arr3==0)*arr2*arr4/(arr5+eps)/100.0)
    a2r.array2raster(output + "_no_CLC", rasterOrigin, pixelWidth, pixelHeight, datatype, result, noDataValue)
    print(output + "_no_CLC")
    """
    result = None

def _cut_pop_layer_get_layer_origin(strd_raster_path_full, strd_raster_path
                                    , strd_vector_path, datatype, NUTS3_feat_id_LIST):
    
    SaveLayerDict = {}
    if strd_raster_path_full != strd_raster_path:
        key_field = "NUTS_ID"
        #feat_id_LIST = [12,13,14]  # 14refers to the feature ID of Vienna
        
        (outRastPath, rasterOrigin2, pxWidth, pxHeight, DatType, arr_pop_cut 
         , noDataVal_, feat_name_dict) = SF.cut_population_layer(
                         NUTS3_feat_id_LIST
                         , strd_vector_path
                         , strd_raster_path_full
                         , strd_raster_path
                         , datatype)
        
        #a2r.array2raster(outRastPath, rasterOrigin2, pxWidth, pxHeight, DatType, arr_pop_cut , noDataVal_)
        SaveLayerDict[outRastPath] = (outRastPath, rasterOrigin2, pxWidth, pxHeight
                                      , DatType, arr_pop_cut , noDataVal_)
        transform = (rasterOrigin2[0], pxWidth, 0.0, rasterOrigin2[1], 0.0, pxHeight)
        ########################################
        # END
        #
        ######################################

    try:     
        if len(transform) != 6:
            load_layer = True
        else:
            load_layer = False
            (RasterYSize, RasterXSize) = arr_pop_cut.shape
        
    except:
        load_layer = True
        
    if load_layer == True: 
        
        #Load (smaller) population layer         
        cutRastDatasource = gdal.Open(strd_raster_path)
        transform = cutRastDatasource.GetGeoTransform()
        RasterXSize = cutRastDatasource.RasterXSize
        RasterYSize = cutRastDatasource.RasterYSize
    
    minx = transform[0]
    maxy = transform[3]
    maxx = minx + transform[1] * RasterXSize
    miny = maxy + transform[5] * RasterYSize
    extent = (minx,maxx,miny,maxy)
    rasterOrigin = (minx, maxy)
    
    return rasterOrigin, extent, SaveLayerDict
  
def _process1(org_data_path, temp_path, strd_raster_path, r1, noDataValue):  
    # cuts SOIL Sealing cuts to same size as population layer, smaller data processing (Values above 100%...)
    
    print("Process 1")
    SaveLayerDict = {}
    in_rast_path = "%s/%s" %(org_data_path, "SS2012.tif")
    datatype='int16'
    out_raster_path = "%s/%s" %(temp_path, "temp1.tif")

    return_tuple = cre.RastExtMod(
                        in_rast_path, strd_raster_path, datatype
                        , out_raster_path, noDataValue, saveAsRaster=False)
    
    if len(return_tuple) > 1:
        (outRastPath, rasterOrigin2, pxWidth, pxHeight
         , DatType, arr_out, noDataVal_) = return_tuple

                         
        if DEBUG == True:
            SaveLayerDict["temp1"] = (outRastPath, rasterOrigin2, pxWidth, pxHeight, DatType, arr_out , noDataVal_)
    else:
        arr_out = return_tuple
    

    arr1 = arr_out
    data_r1 = np.zeros_like(arr1)
    idxM = arr1 > 0
    data_r1[idxM] = arr1[idxM]
    arr1 = None
    arr_out = None
    idxM = None
    data_r1 = np.minimum(100, data_r1)
    #data = (arr1<101)*arr1
    SaveLayerDict["data_r1"] = (r1, rasterOrigin2, pxWidth, pxHeight, datatype, data_r1 , noDataValue)
    #a2r.array2raster(r1, rasterOrigin, pixelWidth, pixelHeight, datatype, data, noDataValue)

    
    print (r1)
    print (data_r1.shape)
    return SaveLayerDict
    
def _process1a(org_data_path, r7, strd_raster_path, noDataValue):
    
    # cuts Corine cuts to same size as population layer, smaller data processing (Values above 100%...)
    # Save as raster layer
    print("Process 1a")
    
    SaveLayerDict = {}
    #print("Process 1a Corine Landcover data")
    in_rast_path = "%s/%s" %(org_data_path, "g100_clc12_V18_5.tif")
    datatype='int16'
    out_raster_path = r7 +"_before"

    (outRastPath, rasterOrigin2, pxWidth, pxHeight, DatType, arr_out, noDataVal_) = cre.RastExtMod(
                        in_rast_path, strd_raster_path, datatype, out_raster_path, noDataValue)
    
    if DEBUG == True:
        SaveLayerDict["out_raster_path"] = (outRastPath, rasterOrigin2
                                  , pxWidth, pxHeight, DatType
                                  , arr_out , noDataVal_)
    
    #RastExtMod(in_rast_path, strd_raster_path, datatype, out_raster_path, noDataValue)
 
    #ds1 = gdal.Open(out_raster_path)
    #b11 = ds1.GetRasterBand(1)
    #arr1 = b11.ReadAsArray()
    
    data_CLC = (CORINE_LANDCOVER_TRANSFORM_MATRIX[arr_out] * 100)
    arr_out = None
    SaveLayerDict['data_CLC'] = (r7, rasterOrigin2, pxWidth, pxHeight
                                 , datatype, data_CLC , noDataValue)
    
    #a2r.array2raster(r7, rasterOrigin, pixelWidth, pixelHeight, datatype, data_CLC, noDataValue)

    print (r7)
    print (data_CLC.shape) 
    return  SaveLayerDict

def _process2(strd_raster_path, pixelWidth, pixelHeight, r2, noDataValue):
    
    # transforms population layer from 1x1 km to 100x100m
    # saves as raster layer
    print("Process 2")
    st = time.time()
    in_raster_path = strd_raster_path
    SaveLayerDict = {}
    datatype = 'float32'
    
    (outRastPath, rasterOrigin2, pxWidth, pxHeight
     , DatType, data_r2, noDataVal_) = hr.HighRes(
                                in_raster_path, pixelWidth, pixelHeight
                                , datatype, r2, noDataValue)
    
    print ("HighRes took: %4.2f sec " % (time.time()-st))
    st1 = time.time()

    a2r.array2raster("%s_before2" %outRastPath, rasterOrigin2
                                 , pxWidth, pxHeight, DatType
                                 , data_r2 , noDataVal_)
    print (np.sum(data_r2))          
    data_r2 = SOHR.CalcAverageBased(data_r2, 10, 6, 1)
    print (np.sum(data_r2))
    print ("CalcAverageBased took: %4.2f sec " % (time.time()-st1))
    
    SaveLayerDict["data_r2"] = (outRastPath, rasterOrigin2, pxWidth, pxHeight
                                , DatType, data_r2 , noDataVal_)
    
    
    print (r2)
    print (data_r2.shape)
    return SaveLayerDict

def _process3(arr1, data_CLC, r3, rasterOrigin, pixelWidth,pixelHeight, noDataValue):
    

    # Calculate sum of soilsailing (100x100 m) for 1x1 km and write that sum on the 100x100 m layer
    # save new raster layer
    print("Process 3")
    
    SaveLayerDict = {}    
    dataType = 'float32'

    #Consider Corine Landcover Data
    #a2r.array2raster(r3 + "dummy_before",rasterOrigin,pixelWidth,pixelHeight,dataType,arr1,noDataValue)
    if DEBUG == True:
        SaveLayerDict[r3+"dummy_before"] = (r3 + "dummy_before",rasterOrigin,pixelWidth,pixelHeight
                                            ,dataType,arr1,noDataValue)
    
    try:
        arr2 = arr1 * data_CLC / 100.0
    except:
        arr2 = arr1
    
    #a2r.array2raster(r3 + "dummy_after",rasterOrigin,pixelWidth,pixelHeight,dataType,arr2,noDataValue)
    if DEBUG == True:
        SaveLayerDict[r3+"dummy_after"] = (r3 + "dummy_after",rasterOrigin,pixelWidth,pixelHeight
                                           ,dataType,arr2,noDataValue)


    st1 = time.time()
    (arr_1_km) = SOHR.CoreLoopSumLowRes(arr2, 10)
    arr1 = None
    arr2 = None
    print("Calc SumLowRes: %4.1f sec " %(time.time() - st1))
    
    
    st1 = time.time()
    #Fast Cython Version
    data_r3 = SOHR.CalcHighRes(arr_1_km, 10)
    print("Calc CalcHighRes: %4.1f sec " %(time.time() - st1))
    

    SaveLayerDict["data_r3"] = (r3,rasterOrigin,
                          pixelWidth, pixelHeight, dataType,
                          data_r3, noDataValue)
    #a2r.array2raster(r3,rasterOrigin,pixelWidth,pixelHeight,dataType,data_r3,noDataValue)
    
    print (r3)
    print (data_r3.shape)
    return SaveLayerDict

def _process4(org_data_path, temp_path, extent, strd_raster_path, r4, noDataValue):
    # takes vector layer (vectors are squares (1x1km - same size as population raster layer))
    # Information stored in Pop_Nuts.shape: NUmber of population per 1km and corresponding NUTS3 region
    # and Energy Demand per Nuts region (vector layer)
    # Store Energy Demand of corresponding NUTS REGION to each 1x1km feature
    SaveLayerDict = {}
    print("Process 4")
    input_vec_path = "%s/%s" %(org_data_path, "Pop_Nuts.shp")
    dict_lyr_path = "%s/%s" %(org_data_path, "NUTS_Demand.shp")
    key_field = "NUTS_ID"
    value_field = "ESPON_TOTA"
    out_field_name = "NutsDem"
    output_lyr_path =  temp_path + os.sep + "temp3.shp"
    inVectorPath = output_lyr_path
    fieldName = "NutsDem"
    dataType = 'float32'
    st1 = time.time()
    qu.query(input_vec_path, extent, dict_lyr_path, key_field, value_field, out_field_name, output_lyr_path)
    print ("Query took: %5.1f sec" % (time.time() - st1))
    st1 = time.time()
    (outRastPath, rasterOrigin2
     , pxWidth, pxHeight, DatType, data_r4, noDataVal_) = ra.rasterize(
                        strd_raster_path, inVectorPath
                        , fieldName, dataType
                        , r4, noDataValue)
    SaveLayerDict["data_r4"] = (outRastPath,rasterOrigin2,
                          pxWidth, pxHeight, DatType,
                          data_r4, noDataVal_)
    print ("Rasterize took: %5.1f sec" % (time.time() - st1))
    print (data_r4.shape)
    
    return SaveLayerDict

def _process5(org_data_path, temp_path, extent, strd_raster_path, r5, noDataValue):
    # takes vector layer (vectors are squares (1x1km - same size as population raster layer))
    # Information stored in Pop_Nuts.shape: NUmber of population per 1km and corresponding NUTS3 region
    # and Population per Nuts region (vector layer), same as the one two lines above
    # Population of corresponding NUTS 3 REGION to each 1x1km feature 

    SaveLayerDict = {}
    print("Process 5")
    input_vec_path = "%s/%s" %(org_data_path, "Pop_Nuts.shp")
    dict_lyr_path = "%s/%s" %(org_data_path, "Pop_Nuts.shp")
    key_field = "NUTS_ID"
    value_field =  "GEOSTAT_gr"
    out_field_name = "NutsPop"
    output_lyr_path =  temp_path + os.sep + "temp5.shp"
    inVectorPath = output_lyr_path
    fieldName = "NutsPop"
    dataType = 'uint32'
    st1 = time.time()

    qu.query(input_vec_path, extent, dict_lyr_path, key_field, value_field, out_field_name, output_lyr_path)    
    print ("Query took: %5.1f sec" % (time.time() - st1))
    st1 = time.time()
    
    
    (outRastPath, rasterOrigin2
     , pxWidth, pxHeight, DatType, data_r5, noDataVal_) = ra.rasterize(
                strd_raster_path, inVectorPath
                , fieldName, dataType
                , r5, noDataValue)
    
    SaveLayerDict["data_r5"] = (outRastPath,rasterOrigin2,
                          pxWidth, pxHeight, DatType,
                          data_r5, noDataVal_)
    print ("Rasterize took: %5.1f sec" % (time.time() - st1))
    print (data_r5.shape)
    return SaveLayerDict


#@profile

class ClassCalcDensity():
    
    def __init__(self, prj_path ):
        
        #Raise error if Data path doesn't exist
        print("Project Path: %s" % prj_path)
        if not os.path.exists(prj_path):
            print("Project Path doesn't exist")
        
        assert(os.path.exists(prj_path))
        self.prj_path = prj_path
        
        # Input data path 
        org_data_path = prj_path  + os.sep + "Original Data"
        if not os.path.exists(org_data_path):
            print("Input data path doesn't exist : %s" % org_data_path)
        
        self.org_data_path = org_data_path
        
        # final output path
        self.prj_path_output    = "%s/output" %prj_path    
        # Path containing processed Data
        self.proc_data_path    = self.prj_path_output  + os.sep + "Processed Data"    
        # Path containing temporal Data
        self.temp_path        = self.prj_path_output  + os.sep + "Temp"
        
        #create if doesn't exist
        if not os.path.exists(self.proc_data_path):
            os.makedirs(self.proc_data_path)
        if not os.path.exists(self.temp_path):
            os.makedirs(self.temp_path)
        
        # define raster size
        self.pixelWidth = 100
        self.pixelHeight = -100 
        
        # input data files
        
        self.strd_vector_path = self.org_data_path+ os.sep + "NUTS3.shp"
        self.strd_raster_path_full = self.org_data_path+ os.sep + "Population.tif"
        self.strd_raster_path = "%s_small.tif" % self.strd_raster_path_full[:-4]
        
        #outputs
        
        self.r1                = self.proc_data_path + os.sep + "ss_pop_cut.tif"
        self.r2                = self.proc_data_path + os.sep + "Pop_1km_100m.tif"
        self.r3                = self.proc_data_path + os.sep + "sum_ss_1km.tif"
        #r4                = proc_data_path + os.sep + "Dem_in_Nuts.tif"
        self.r4                = self.temp_path + os.sep + "temp4.tif"
        self.r5                = self.proc_data_path + os.sep + "Pop_in_Nuts.tif"
        self.r6                = self.proc_data_path + os.sep + "CorineLU.tif"
        self.r7                = self.proc_data_path + os.sep + "CorineLU_cut.tif"
        
        self.output            = self.proc_data_path + os.sep + "demand_v2.tif" 
      
      
        # array2raster output datatype
        self.datatype = 'int32'
        
    def main_process(self, NUTS3_feat_id_LIST):
        
        
        self.NUTS3_feat_id_LIST = NUTS3_feat_id_LIST
        
        start_time = time.time()
        

        
        del_temp_path    = True
        process1           = True
        process1a          = True
        process2           = True
        process3           = True
        process4         = True
        process5        = True
    
        
        if del_temp_path:    
            if os.path.exists(self.temp_path):
                shutil.rmtree(self.temp_path)   
            if not os.path.exists(self.temp_path):
                os.makedirs(self.temp_path)    
        if 0==1:
            if os.path.exists(self.r1):
                process1 = False
            if os.path.exists(self.r2):
                process2 = False
            if os.path.exists(self.r3):
                process3 = False
            if os.path.exists(self.r4):
                process4 = False
            if os.path.exists(self.r5):
                process5 = False
        
        
        # common parameters
        noDataValue = -17.3
        #Standard population raster layer
        # cut standard population raster
        """
        """
        SaveLayerDict = {}
        
        rasterOrigin, extent, SaveLayerDict_ = _cut_pop_layer_get_layer_origin(self.strd_raster_path_full
                                                        , self.strd_raster_path
                                                        , self.strd_vector_path, self.datatype, self.NUTS3_feat_id_LIST)
        
        del_keys = []
        for k in list(SaveLayerDict_.keys()):
            LL = SaveLayerDict_[k]
            a2r.array2raster(LL[0], LL[1], LL[2], LL[3], LL[4], LL[5] , LL[6])
            del LL
            #SaveLayerDict[k] = SaveLayerDict_[k]
            del_keys.append(k)
            #for k in del_keys:
            del SaveLayerDict_[k]
            
    
        print("Preprepartion took: %4.1f " %(time.time() - start_time))
    
        if process1:
            # cuts SOIL Sealing cuts to same size as population layer, smaller data processing (Values above 100%...)
            # Save as raster layer
            
            st = time.time()
            print("\nProcess 1 SoilSealing")
            
            SaveLayerDict_ = _process1(self.org_data_path, self.temp_path, self.strd_raster_path, self.r1, noDataValue)
            
            for k in list(SaveLayerDict_.keys()):
                print (k)
                SaveLayerDict[k] = SaveLayerDict_[k]
                del SaveLayerDict_[k]
                (r,c) = SaveLayerDict[k][5].shape
            
            elapsed_time = time.time() - st
            print("Process 1 took: %4.1f seconds" %elapsed_time)
        
        if process1a and (process1 or process3):      
            # cuts Corine cuts to same size as population layer, smaller data processing (Values above 100%...)
            # Save as raster layer
            st = time.time()
            print("\nProcess 1a Corine Landcover data")
            SaveLayerDict_ = _process1a(self.org_data_path, self.r7, self.strd_raster_path, noDataValue)
            
            for k in list(SaveLayerDict_.keys()):
                print (k)
                SaveLayerDict[k] = SaveLayerDict_[k]
                del SaveLayerDict_[k]
            
    
            
            elapsed_time = time.time() - st
            print("Process 1a took: %4.1f seconds" %elapsed_time)
            
        if process2:
            # transforms population layer from 1x1 km to 100x100m
            # saves as raster layer
            st = time.time()
            print("\nProcess 2")
            
            SaveLayerDict_ = _process2(self.strd_raster_path, self.pixelWidth
                                       , self.pixelHeight, self.r2, noDataValue)
            for k in list(SaveLayerDict_.keys()):
                print (k)
                if k == "data_r2" and EXPORT_LAYERS == True:
                    print ("Eport %s" %k)
                    stx = time.time()
                    LL = SaveLayerDict_[k]
                    a2r.array2raster(LL[0], LL[1], LL[2], LL[3], LL[4], LL[5] , LL[6])
                    print (time.time() -stx)
                    # Replace Matrix by Path
                    SaveLayerDict_[k] = (LL[0], LL[1], LL[2], LL[3], LL[4], LL[0] , LL[6]) 
                SaveLayerDict[k] = SaveLayerDict_[k]
                del SaveLayerDict_[k]
                
            elapsed_time = time.time() - st
            print("Process 2 took: %4.1f seconds" %elapsed_time)
    
    
            
        if process3:
            # Calculate sum of soilsailing (100x100 m) for 1x1 km and write that sum on the 100x100 m layer
            # save new raster layer
            st = time.time()
            print("\nProcess 3")
            
            #outRasterPath = "%s/%s" %(temp_path, "temp2.tif")
            dataType = 'float32'
            try:
                data_r1 = SaveLayerDict["data_r1"][5]
                if (r,c) == data_r1.shape:
                    arr1 = np.zeros_like(data_r1)
                    arr1[:, :] = data_r1 
                    reload_data = False
                else:
                    reload_data = True
            except:
                reload_data = True
            if reload_data == True:
                input_value_raster = self.r1
                arr1 = SF.rrl(input_value_raster, data_type=dataType)
                """ds1 = gdal.Open(input_value_raster)
                b11 = ds1.GetRasterBand(1)
                arr1 = b11.ReadAsArray().astype(dataType)
                """
            data_CLC = SaveLayerDict["data_CLC"][5]
            
            SaveLayerDict_ = _process3(arr1, data_CLC, self.r3, rasterOrigin
                                       , self.pixelWidth, self.pixelHeight, noDataValue)
            del arr1
            for k in list(SaveLayerDict_.keys()):
                print (k)
                if k == "data_r3" and EXPORT_LAYERS == True:
                    print ("Eport %s" %k)
                    stx = time.time()
                    LL = SaveLayerDict_[k]
                    a2r.array2raster(LL[0], LL[1], LL[2], LL[3], LL[4], LL[5] , LL[6])
                    print (time.time() -stx)
                    # Replace Matrix by Path
                    SaveLayerDict_[k] = (LL[0], LL[1], LL[2], LL[3], LL[4], LL[0] , LL[6])  
                SaveLayerDict[k] = SaveLayerDict_[k]
                del SaveLayerDict_[k]
            
            elapsed_time3 = time.time() - st
    
            print("Process 3 took: %4.1f seconds" %elapsed_time3)
        
        if process4:
            # takes vector layer (vectors are squares (1x1km - same size as population raster layer))
            # Information stored in Pop_Nuts.shape: NUmber of population per 1km and corresponding NUTS3 region
            # and Energy Demand per Nuts region (vector layer)
            # Store Energy Demand of corresponding NUTS REGION to each 1x1km feature
            st = time.time()
            print("\nProcess 4")
            
            SaveLayerDict_ = _process4(self.org_data_path, self.temp_path, extent
                                       , self.strd_raster_path, self.r4, noDataValue)
            for k in list(SaveLayerDict_.keys()):
                print (k)
                if k == "data_r4" and EXPORT_LAYERS == True:
                    print ("Eport %s" %k)
                    stx = time.time()
                    LL = SaveLayerDict_[k]
                    a2r.array2raster(LL[0], LL[1], LL[2], LL[3], LL[4], LL[5] , LL[6])
                    print (time.time() -stx)
                    # Replace Matrix by Path
                    SaveLayerDict_[k] = (LL[0], LL[1], LL[2], LL[3], LL[4], LL[0] , LL[6]) 
                SaveLayerDict[k] = SaveLayerDict_[k]
                del SaveLayerDict_[k]
                
            elapsed_time = time.time() - st
            print("Process 4 took: %4.1f seconds" %elapsed_time)
           
        if process5:
            # takes vector layer (vectors are squares (1x1km - same size as population raster layer))
            # Information stored in Pop_Nuts.shape: NUmber of population per 1km and corresponding NUTS3 region
            # and Population per Nuts region (vector layer), same as the one two lines above
            # Population of corresponding NUTS 3 REGION to each 1x1km feature 
            st = time.time()
            print("\nProcess 5") 
            SaveLayerDict_ = _process5(self.org_data_path, self.temp_path
                                       , extent, self.strd_raster_path, self.r5, noDataValue)
            for k in list(SaveLayerDict_.keys()):
                print (k)
                if k == "data_r5" and EXPORT_LAYERS == True:
                    print ("Eport %s" %k)
                    stx = time.time()
                    LL = SaveLayerDict_[k]
                    a2r.array2raster(LL[0], LL[1], LL[2], LL[3], LL[4], LL[5] , LL[6])
                    print (time.time() -stx)
                    # Replace Matrix by Path
                    SaveLayerDict_[k] = (LL[0], LL[1], LL[2], LL[3], LL[4], LL[0] , LL[6]) 
                SaveLayerDict[k] = SaveLayerDict_[k]
                del SaveLayerDict_[k]
    
            elapsed_time = time.time() - st
            print("Process 5 took: %4.1f seconds" %elapsed_time)
    
                           
        print ("Outputfile: %s" % self.output)
        st = time.time()
        HeatDensity(data_r1, SaveLayerDict["data_r2"][5]
                , SaveLayerDict["data_r3"][5]
                , SaveLayerDict["data_r4"][5]
                , SaveLayerDict["data_r5"][5]
                , data_CLC, rasterOrigin, self.output)
    
        print("HeatDensity process took: %4.1f seconds" %(time.time() - st))
        elapsed_time = time.time() - start_time
        print("The whole process took: %4.1f seconds" %elapsed_time)
    
    
        print ("Export Layers:")
        st = time.time()
        for k in list(SaveLayerDict.keys()):
            st1 = time.time()
            LL = SaveLayerDict[k]
            print (LL[0])
            if type(LL[5]) is str:
                pass
                print ("already exported")
            else:
                try:
                    a2r.array2raster(LL[0], LL[1], LL[2], LL[3], LL[4], LL[5] , LL[6])
                except Exception as e:
                    print (e)
            del SaveLayerDict[k]
            print (time.time() - st1)
        print("Process Export Layers took: %4.1f seconds" %(time.time() - st))    
            
            
            
        # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX Close XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        if del_temp_path:
            if os.path.exists(self.temp_path):
                shutil.rmtree(self.temp_path)
        print ("Done!")
        return


    
if __name__ == "__main__":
    
    main_process()