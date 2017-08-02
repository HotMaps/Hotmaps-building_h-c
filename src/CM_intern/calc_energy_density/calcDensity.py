import numpy as np
import shutil
import sys, os, time, gdal, ogr
import csv
sys.path.insert(0, "../..")

import  CM_intern.common_modules.Subfunctions as SF
import  CM_intern.common_modules.changeRastExt as cre   # import RastExtMod

import  CM_intern.calc_energy_density.modules.higherRes as hr        # import HighRes
import  CM_intern.calc_energy_density.modules.query as qu
import  CM_intern.calc_energy_density.modules.rasterize as ra

#from zonal_statistics import ZonalStat

import CM_intern.common_modules.array2raster as a2r
import CM_intern.common_modules.cliprasterlayer as crl
import CM_intern.calc_energy_density.modules.cython_files.SumOfHighRes_64 as SOHR

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
    a2r.array2rasterfile(output, rasterOrigin
                         , pixelWidth, pixelHeight
                         , datatype, result, noDataValue)
    print(output)
    
    """
    result = (arr5>0)*((arr3>0)*arr1*arr2*arr4/(arr3+eps)/(arr5+eps) + (arr3==0)*arr2*arr4/(arr5+eps)/100.0)
    a2r.array2raster(output + "_no_CLC", rasterOrigin, pixelWidth, pixelHeight, datatype, result, noDataValue)
    print(output + "_no_CLC")
    """
    result = None


  
def _process1(TobeClippedRasterPath, temp_output_path, baseRasterPath
              , outputFileName, noDataValue):  
    # cuts SOIL Sealing cuts to same size as population layer, smaller data processing (Values above 100%...)
    
    print("Process 1")
    SaveLayerDict = {}
    datatype='int16'
    
    

    return_tuple = cre.RastExtMod(
                        TobeClippedRasterPath, baseRasterPath, datatype
                        , temp_output_path, noDataValue, saveAsRaster=False)
    
    if len(return_tuple) > 1:
        (outRastPath, rasterOrigin2, pxWidth, pxHeight
         , DatType, arr_out, noDataVal_) = return_tuple

                         
        if DEBUG == True:
            SaveLayerDict["temp_ss_pop_cut"] = (outRastPath, rasterOrigin2, pxWidth, pxHeight, DatType, arr_out , noDataVal_)
    else:
        arr_out = return_tuple
    

    idxM = arr_out > 0
    # Soil sealing as for Building-Floor-Area.Proxy
    data_ss_pop_cut = np.zeros_like(arr_out)
    data_ss_pop_cut[idxM] = arr_out[idxM]
    del arr_out, idxM
    
    data_ss_pop_cut = np.minimum(100, data_ss_pop_cut)
    data_ss_pop_cut = np.maximum(0, data_ss_pop_cut)

    SaveLayerDict["data_ss_pop_cut"] = (outputFileName, rasterOrigin2, pxWidth, pxHeight, datatype, data_ss_pop_cut , noDataValue)
    
    print (outputFileName)
    print (data_ss_pop_cut.shape)
    return SaveLayerDict
    
def _process1a(TobeClippedRasterPath, outputFileName, base_raster_path
               , noDataValue, saveAsRaster=False):
    """
     cuts Corine Landuse/Landcover to same size as population layer)
     Processes to Information contained in the CLU files using the 
     CORINE_LANDCOVER_TRANSFORM_MATRIX
     Save as raster layer
    """
    print("Process Corine Landuse layer")
    
    SaveLayerDict = {}
    #print("Process 1a Corine Landcover data")
    datatype='int16'
    

    (outRastPath, rasterOrigin2, pxWidth, pxHeight, DatType, arr_out, noDataVal_) = cre.RastExtMod(
                        TobeClippedRasterPath, base_raster_path, datatype, outputFileName, noDataValue)
    
    if DEBUG == True:
        SaveLayerDict["data_CLC_before"] = (outRastPath + "_before", rasterOrigin2
                                  , pxWidth, pxHeight, DatType
                                  , arr_out , noDataVal_)
    
    # Perform transformation of Corine Data -> Landuse Indikator to Building-Floor-Area.Proxy
    data_CLC = (CORINE_LANDCOVER_TRANSFORM_MATRIX[arr_out] * 100)
    if DEBUG != True:
        del arr_out
    SaveLayerDict['data_CLC'] = (outRastPath, rasterOrigin2
                                 , pxWidth, pxHeight, datatype
                                 , data_CLC , noDataValue)

    print (outRastPath)
    print (data_CLC.shape) 
    return  SaveLayerDict

def _process2(in_raster_path, pixelWidth, pixelHeight
              , out_raster_path, noDataValue):
    
    # transforms population layer from 1x1 km to 100x100m
    # return array
    print("Process 2")
    st = time.time()
    SaveLayerDict = {}
    datatype = 'float32'
    print("Start hr.HighRes C-Function")
    (outRastPath, rasterOrigin2, pxWidth, pxHeight
     , DatType, data_pop100, noDataVal_) = hr.HighRes(
                                in_raster_path, pixelWidth, pixelHeight
                                , datatype, out_raster_path, noDataValue)
    
    print ("HighRes took: %4.2f sec " % (time.time()-st))
    st1 = time.time()
    if DEBUG:
        a2r.array2rasterfile("%s_before2" %outRastPath, rasterOrigin2
                                 , pxWidth, pxHeight, DatType
                                 , data_pop100 , noDataVal_)
    
    print (np.sum(data_pop100))          
    data_pop100 = SOHR.CalcAverageBased(data_pop100, 10, 6, 1)
    print (np.sum(data_pop100))
    print ("CalcAverageBased took: %4.2f sec " % (time.time()-st1))
    
    SaveLayerDict["data_pop100"] = (outRastPath, rasterOrigin2, pxWidth, pxHeight
                                , DatType, data_pop100 , noDataVal_)
    
    
    print (out_raster_path)
    print (data_pop100.shape)
    return SaveLayerDict

def _process3(data_SS, data_CLC, outputFileName
              , rasterOrigin, pixelWidth, pixelHeight, noDataValue):
    

    # Calculate sum of soilsailing (100x100 m) corrected by CLC data for 1x1 km 
    # and write that sum on the 100x100 m layer
    
    # save new raster layer
    print("Process 3")
    
    SaveLayerDict = {}    
    dataType = 'float32'

    #Consider Corine Landcover Data
    if DEBUG == True:
        SaveLayerDict[outputFileName + "dummy_before"] = (outputFileName + "dummy_before"
                                                          , rasterOrigin, pixelWidth, pixelHeight
                                            ,dataType, data_SS, noDataValue)
    
    try:
        data_SS_CLC = data_SS * data_CLC / 100.0
    except:
        data_SS_CLC = data_SS
    
    
    if DEBUG == True:
        SaveLayerDict[outputFileName + "dummy_after"] = (outputFileName + "dummy_after"
                                                         , rasterOrigin, pixelWidth, pixelHeight
                                           ,dataType, data_SS_CLC, noDataValue)


    st1 = time.time()
    (data_SS_CLC_1_km) = SOHR.CoreLoopSumLowRes(data_SS_CLC, 10)
    del data_SS, data_SS_CLC
    print("Calc SumLowRes: %4.1f sec " %(time.time() - st1))
    
    
    st1 = time.time()
    #Fast Cython Version
    # Calculate HighResulution File
    data_SS_CLC = SOHR.CalcHighRes(data_SS_CLC_1_km, 10)
    print("Calc CalcHighRes: %4.1f sec " %(time.time() - st1))
    

    SaveLayerDict["data_SS_CLC"] = (outputFileName, rasterOrigin,
                          pixelWidth, pixelHeight, dataType,
                          data_SS_CLC, noDataValue)
    
    print (outputFileName)
    print (data_SS_CLC.shape)
    return SaveLayerDict

def _process4(input_data_path, temp_path, extent
              , base_raster_path
              , r4, noDataValue):
    # takes vector layer (vectors are squares (1x1km - same size as population raster layer))
    # Information stored in 1x1kmDensity_Nuts.shape: Number of population per 1km and corresponding NUTS3 region
    # and Energy Demand per Nuts region (vector layer)
    # Store Information of corresponding NUTS REGION to each 1x1km feature
    SaveLayerDict = {}
    print("Process 4")
    # 1x1 km raster
    input_RASTvec_path = "%s/%s" %(input_data_path, "1x1kmDensity_Nuts.shp")
    
    
    dict_lyr_path = "%s/%s" %(input_data_path, "NUTS3.shp")
    key_field = "NUTS_ID"
    value_field = "IDNUMBER"
    out_field_name = "NutsDem"
    output_lyr_path =  temp_path + os.sep + "temp3.shp"
    inVectorPath = output_lyr_path
    fieldName = "NutsDem"
    dataType = 'float32'
    
    
    # READ NUTS3 Data
    
    Nuts3DatafileSet = "%s/NUTS3_data.csv" % input_data_path
    with open(Nuts3DatafileSet, 'r') as csvfile:
        datareader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for i, row in enumerate(datareader):
            if i == 0:
                VarNames = row
            elif i == 1:
                VarType= row
                break 
        dtype_ = []
        for i in range(len(VarNames)):
            if VarType[i].startswith("S") and sys.version_info[0] == 3 :
                VarType[i] = VarType[i].replace("S", "U")
            dtype_.append((VarNames[i], VarType[i]))


    NUTS3DataSet = np.genfromtxt(Nuts3DatafileSet, dtype_
                            , delimiter=","
                            , skip_header=2)
    
    st1 = time.time()
    MapNuts3Array = qu.query(input_RASTvec_path, extent, dict_lyr_path, key_field, value_field
             , out_field_name, output_lyr_path)
    print ("Query took: %5.1f sec" % (time.time() - st1))
    st1 = time.time()
    (outRastPath, rasterOrigin2
     , pxWidth, pxHeight, DatType, data_r4, noDataVal_) = ra.rasterize(
                        base_raster_path, inVectorPath
                        , fieldName, dataType
                        , r4, noDataValue, saveAsRaster=False)
    data_r4 = data_r4.astype("int")
    SaveLayerDict["data_r4"] = (outRastPath,rasterOrigin2,
                          pxWidth, pxHeight, DatType,
                          data_r4, noDataVal_)
    
    data_array_ = np.zeros_like(data_r4)
    for i in range(4, len(NUTS3DataSet.dtype)):
        data_array_= NUTS3DataSet[VarNames[i]][data_r4]
        SaveLayerDict["data_%s" % VarNames[i]] = ("%s/%s.tiff" %(os.path.dirname(outRastPath), VarNames[i])
                          , rasterOrigin2,
                          pxWidth, pxHeight, DatType,
                          data_array_, noDataVal_) 
    print ("Rasterize took: %5.1f sec" % (time.time() - st1))
    print (data_r4.shape)
    #sys.exit()
    return SaveLayerDict, NUTS3DataSet, MapNuts3Array

def _process5(org_data_path, temp_path, extent, base_raster_path, r5, noDataValue):
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
                base_raster_path, inVectorPath
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
        
        # No Data Value (-17.3 to distinguesh between 0 and no Data)
        # Not sure if No Data get this value or if this value is exported as NoData
        self.noDataValue = -17.3
        # input data files
        
        # Standard Vector layer (Nuts 3 shape file)
        self.strd_vector_path = "%s/NUTS3.shp" % self.org_data_path
        # Standard Raster layer 
        # Population Layer
        self.strd_raster_path_full = "%s/Population.tif" % self.org_data_path
        # Clipped Raster layer
        self.base_raster_path = "%s_clipped.tif" % self.strd_raster_path_full[:-4]
        
        #outputs
        
        #Soil Sealing and Population
        self.ss_cut        = self.proc_data_path + os.sep + "ss_cut.tif"
        
        self.pop100    = self.proc_data_path + os.sep + "Pop_1km_100m.tif"
        self.SSCLU_1km = self.proc_data_path + os.sep + "CLU_ss_1km.tif"

        self.r4        = self.temp_path + os.sep + "temp4.tif"
        self.r5        = self.proc_data_path + os.sep + "Pop_in_Nuts.tif"
        #self.CLU               = self.proc_data_path + os.sep + "CorineLU.tif"
        self.CLU_cut   = self.proc_data_path + os.sep + "CorineLU_cut.tif"
        
        self.output    = self.proc_data_path + os.sep + "demand_v2.tif" 
      
      
        # array2raster output datatype
        self.datatype = 'int32'
        
    def main_process(self, NUTS3_feat_id_LIST):
        
        
        self.NUTS3_feat_id_LIST = NUTS3_feat_id_LIST
        
        start_time = time.time()
        

        
        del_temp_path    = True
        process1           = False
        process1a          = False
        process2           = False
        process3           = False
        
        #"""
        process1           = True
        process1a          = True
        process2           = True
        process3           = True
        #"""
        process4         = True
        process5        = True
    
        
        
        if del_temp_path:    
            if os.path.exists(self.temp_path):
                shutil.rmtree(self.temp_path)   
        
        if not os.path.exists(self.temp_path):
                os.makedirs(self.temp_path) 
                       
        if 0==1:
            if os.path.exists(self.ss_cut):
                process1 = False
            if os.path.exists(self.pop100):
                process2 = False
            if os.path.exists(self.SSCLU_1km):
                process3 = False
            if os.path.exists(self.r4):
                process4 = False
            if os.path.exists(self.r5):
                process5 = False
        

        
        SaveLayerDict = {}
        
        # Clip Raster layer based on list of vector layer features (Selected NUTS3 Regions
        Vctr_key_field = "NUTS_ID"
        """
        SaveLayerDict_ contains Key: filename of output raster file (OutputRasterFile)
                List: [outRastPath, rasterOrigin2, pxWidth
                , pxHeight, DatType, arr_pop_cut , noDataVal]  
        """
        SaveLayerDict_, rasterOrigin, extent = crl.clip_raster_layer_vctr_feat(self.strd_raster_path_full
                                                        , self.base_raster_path
                                                        , self.strd_vector_path, self.NUTS3_feat_id_LIST
                                                        , Vctr_key_field, self.datatype)
        
        del_keys = []
        for k in list(SaveLayerDict_.keys()):
            LL = SaveLayerDict_[k]
            # Export rasterfile
            a2r.array2rasterfileList(LL)
            del LL
            #SaveLayerDict[k] = SaveLayerDict_[k]
            del_keys.append(k)
            #for k in del_keys:
            del SaveLayerDict_[k]
            
    
        print("Preparation (Clip initial raster file) took: %4.1f " %(time.time() - start_time))
    
        if process1:
            # cuts SOIL Sealing cuts to same size as population layer, smaller data processing (Values above 100%...)
            # Save as raster layer
            st = time.time()
            print("\nProcess 1: Cut SoilSealing")
            TobeClippedRasterPath = "%s/%s" %(self.org_data_path, "SS2012.tif")
            TempOutPutFileName = "temp1"
            temp_output_path = "%s/%s.tif" %(self.temp_path, TempOutPutFileName)
            
            SaveLayerDict_ = _process1(TobeClippedRasterPath, temp_output_path
                                       , self.base_raster_path, self.ss_cut, self.noDataValue)
            
            for k in list(SaveLayerDict_.keys()):
                print (k)
                SaveLayerDict[k] = SaveLayerDict_[k]
                del SaveLayerDict_[k]
                (row,col) = SaveLayerDict[k][5].shape
            
            elapsed_time = time.time() - st
            print("Process 1 took: %4.1f seconds" %elapsed_time)
        
        if process1a and (process1 or process3):      
            # cuts Corine cuts to same size as population layer, smaller data processing (Values above 100%...)
            # Save as raster layer
            st = time.time()
            print("\nProcess 1a: Corine Landcover data")
            TobeClippedRasterPath = "%s/%s" %(self.org_data_path, "g100_clc12_V18_5.tif")
            SaveLayerDict_ = _process1a(TobeClippedRasterPath, self.CLU_cut, self.base_raster_path, self.noDataValue)
            
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
            
            SaveLayerDict_ = _process2(self.base_raster_path, self.pixelWidth
                                       , self.pixelHeight, self.pop100, self.noDataValue)
            for k in list(SaveLayerDict_.keys()):
                print (k)
                if k == "data_pop100" and EXPORT_LAYERS == True:
                    print ("Export %s" %k)
                    stx = time.time()
                    LL = SaveLayerDict_[k]
                    a2r.array2rasterfileList(LL)
                    print (time.time() -stx)
                    # Replace Matrix by Path
                    SaveLayerDict_[k] = (LL[0], LL[1], LL[2], LL[3], LL[4], LL[0] , LL[6])
                SaveLayerDict[k] = SaveLayerDict_[k]
                del SaveLayerDict_[k]
                
            elapsed_time = time.time() - st
            print("Process 2 took: %4.1f seconds" %elapsed_time)
            
            
        if process3:
            # Calculate density function of proxy for heat/floor area distribution
            # CLU Transformation time  soilsailing (100x100 m) 
            # -> Calc sum for 1x1 km and write that sum on the 100x100 m layer
            # return array (optional save new raster layer)
            st = time.time()
            print("\nProcess 3")
            
            #outRasterPath = "%s/%s" %(temp_path, "temp2.tif")
            dataType = 'float32'
            try:
                data_ss_pop_cut = SaveLayerDict["data_ss_pop_cut"][5]
                if (row,col) == data_ss_pop_cut.shape:
                    
                    if DEBUG:
                        # create copy to ensure that data of data_ss_pop_cut are not changed
                        # -> which are later exported for debug reasons
                        data_ss_pop_cut_ = data_ss_pop_cut.copy() 
                    else: 
                        data_ss_pop_cut_ = data_ss_pop_cut
                        
                    reload_data = False
                else:
                    reload_data = True
            except:
                reload_data = True
            
            if reload_data == True:
                data_ss_pop_cut_ = SF.read_raster_layer(self.ss_cut, data_type=dataType)

            data_CLC = SaveLayerDict["data_CLC"][5]
            
            SaveLayerDict_ = _process3(data_ss_pop_cut_, data_CLC
                                       , self.SSCLU_1km, rasterOrigin
                                       , self.pixelWidth, self.pixelHeight, self.noDataValue)
            if DEBUG:
                del data_ss_pop_cut_
            for k in list(SaveLayerDict_.keys()):
                print (k)
                if k == "data_SS_CLC" and EXPORT_LAYERS == True:
                    print ("Eport %s" %k)
                    stx = time.time()
                    LL = SaveLayerDict_[k]
                    a2r.array2rasterfileList(LL)
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
            print("\nProcess 4: Transform NUTS3 Info to 1x1km")
            
            (SaveLayerDict_ , NUTS3DataSet, MapNuts3Array
                ) = _process4(self.org_data_path, self.temp_path, extent
                                       , self.base_raster_path, self.r4
                                       , self.noDataValue)
            for k in list(SaveLayerDict_.keys()):
                print (k)
                if k == "data_r4" and EXPORT_LAYERS == True:
                    print ("Eport %s" %k)
                    stx = time.time()
                    LL = SaveLayerDict_[k]
                    a2r.array2rasterfileList(LL)
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
            """
            SaveLayerDict_ = _process5(self.org_data_path, self.temp_path
                                       , extent, self.base_raster_path, self.r5, self.noDataValue)
            for k in list(SaveLayerDict_.keys()):
                print (k)
                if k == "data_r5" and EXPORT_LAYERS == True:
                    print ("Eport %s" %k)
                    stx = time.time()
                    LL = SaveLayerDict_[k]
                    a2r.array2rasterfile(LL[0], LL[1], LL[2], LL[3], LL[4], LL[5] , LL[6])
                    print (time.time() -stx)
                    # Replace Matrix by Path
                    SaveLayerDict_[k] = (LL[0], LL[1], LL[2], LL[3], LL[4], LL[0] , LL[6]) 
                SaveLayerDict[k] = SaveLayerDict_[k]
                del SaveLayerDict_[k]
            """
            elapsed_time = time.time() - st
            
            SaveLayerDict["data_r5"] = SaveLayerDict["data_POP2012"] 
            print("Process 5 took: %4.1f seconds" %elapsed_time)
    
                       
        print ("Outputfile: %s" % self.output)
        st = time.time()
        HeatDensity(data_ss_pop_cut, SaveLayerDict["data_pop100"][5]
                , SaveLayerDict["data_SS_CLC"][5]
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
                    a2r.array2rasterfile(LL[0], LL[1], LL[2], LL[3], LL[4], LL[5] , LL[6])
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
    

    
    print(sys.version_info)
    pr_path = "/home/simulant/workspace/project/Hotmaps_DATA/heat_density_map/"
    
    
    #Nuts3 Regions
    NUTS3_feat_id_LIST = [14]  # 14refers to the feature ID of Vienna
    NUTS3_feat_id_LIST = range(0,20000)  # 14refers to the feature ID of Vienna
    NUTS3_feat_id_LIST = range(12,15)
    NUTS3_feat_id_LIST = [14]
    CD = ClassCalcDensity(pr_path)
    CD.main_process(NUTS3_feat_id_LIST)

    
    print("Done!")