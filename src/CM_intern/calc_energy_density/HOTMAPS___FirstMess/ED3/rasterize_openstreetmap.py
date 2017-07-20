'''
Created on May 2, 2017

@author: simulant
'''
import os, glob
import time
import sys, os, time, gdal, ogr
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image


import query as qu
import rasterize2 as ra
import array2raster as a2r
import Subfunctions as SF
from countries import COUNTRIES

if True:
    #commun_lyr_path = "/home/simulant/ag_lukas/personen/Mostafa/openstreetmap/data/Communal3035.shp"
    #commun_lyr_path = "./openstreetmap/Communal3035.shp"
    #building_lyr_base_path = "/home/simulant/ag_lukas/personen/Andreas/Openstreetmapdata"
    building_lyr_path2 = "../openstreetmap/extract/"
    
    #extent_lyr_path = "./openstreetmap/extent.shp"

    

country_file_list = []
country_file_list_lc = []
for (dirpath,dirnames,filenames) in os.walk(building_lyr_path2):
    for ele in dirnames:
        if "austr" not in ele.lower():
            pass
            #continue
        c_path = "%s%s/" %(dirpath, ele)
        file_list = glob.glob('%s*buildin*_3035.shp' % c_path)
        #print (len(file_list))
        if file_list == []:
            print ("No building_layer file: %s" %c_path)
        #for file_ in file_list:

        country_file_list.extend(file_list)
        #country_file_list_lc.extend(file_list.lower())

#country_file_list = country_file_list[1:10]   
print (country_file_list)

feat_id_LIST = [14]  # 14refers to the feature ID of Vienna
#feat_id_LIST = range(0,20000)  # 14refers to the feature ID of Vienna
feat_id_LIST = range(0,20000)

EXPORT_LAYERS = False

def _process5(org_data_path, OSM_building_file, temp_path, extent, strd_raster_path
              , r5, noDataValue, BUILDNAME_DICT):
    # takes vector layer (vectors are squares (1x1km - same size as population raster layer))
    # Information stored in Pop_Nuts.shape: NUmber of population per 1km and corresponding NUTS3 region
    # and Population per Nuts region (vector layer), same as the one two lines above
    # Population of corresponding NUTS 3 REGION to each 1x1km feature 

    
    SaveLayerDict = {}
    """print("Process 4")
    input_vec_path = "%s/%s" %(org_data_path, "Pop_Nuts.shp")
    dict_lyr_path = "%s/%s" %(org_data_path, "NUTS_Demand.shp")
    key_field = "NUTS_ID"
    value_field = "ESPON_TOTA"
    out_field_name = "NutsDem"
    output_lyr_path =  temp_path + os.sep + "temp5.shp"
    inVectorPath = output_lyr_path
    fieldName = "NutsDem"
    dataType = 'float32'
    st1 = time.time()
    qu.query(input_vec_path, extent, dict_lyr_path, key_field, value_field, out_field_name, output_lyr_path)
    """
    
    
    SaveLayerDict = {}
    #print("Process 5")
    input_vec_path = OSM_building_file
    dict_lyr_path = OSM_building_file
    key_field = "NUTS_ID"
    value_field =  "GEOSTAT_gr"
    out_field_name = "NutsPop"
    output_lyr_path =  temp_path + os.sep + "temp5.shp"
    inVectorPath = output_lyr_path
    fieldName = "NutsPop"
    dataType = 'float64'
    st1 = time.time()
    
    
    
    
    (outRastPath, rasterOrigin2
     , pxWidth, pxHeight, DatType, data_r5, noDataVal_, BUILDNAME_DICT) = ra.rasterize(
                strd_raster_path, input_vec_path
                , "__AREA__", "float32"
                , r5, noDataValue, RESOLUTION = 100
                , BUILDNAME_DICT=BUILDNAME_DICT)
     
    
    SaveLayerDict["data_r5"] = (outRastPath,rasterOrigin2,
                          pxWidth, pxHeight, DatType,
                          data_r5, noDataVal_)
    print ("    Rasterize took: %5.1f sec" % (time.time() - st1))
    #print (data_r5.shape)
    return SaveLayerDict, BUILDNAME_DICT

def _cut_pop_layer_get_layer_origin(strd_raster_path_full, strd_raster_path
                                    , strd_vector_path, datatype):
    
    SaveLayerDict = {}
    if strd_raster_path_full != strd_raster_path:
        key_field = "NUTS_ID"
        #feat_id_LIST = [12,13,14]  # 14refers to the feature ID of Vienna
        
        (outRastPath, rasterOrigin2, pxWidth, pxHeight, DatType, arr_pop_cut , noDataVal_
         , feat_name_dict) = SF.cut_population_layer(
                         feat_id_LIST
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
    
    return rasterOrigin, extent, SaveLayerDict, feat_name_dict

#@profile
def main_process():
    
    BUILDNAME_DICT = []
    start_time = time.time()
    
    pixelWidth = 100
    pixelHeight = -100
    
    if True:
        #prj_path    = "/home/simulant/ag_lukas/personen/Mostafa/HeatDensityMap - Copy"
        prj_path    = "./DATA"
        prj_path_output    = "%s/output_OSM" %prj_path    
       
    org_data_path    = prj_path  + os.sep + "Original Data"
    proc_data_path    = prj_path_output  + os.sep + "Processed Data"    
    temp_path        = prj_path_output  + os.sep + "Temp"
    proc_data_path_csv = "%s/csv" % proc_data_path
    if not os.path.exists(proc_data_path):
        os.makedirs(proc_data_path)
    if not os.path.exists(temp_path):
        os.makedirs(temp_path)
    if not os.path.exists(proc_data_path_csv):
        os.makedirs(proc_data_path_csv)
    # inputs
    strd_vector_path = org_data_path+ os.sep + "NUTS3.shp"
    strd_raster_path_full = org_data_path+ os.sep + "Population.tif"
    strd_raster_path = "%s/%s_small.tif" % (temp_path, strd_raster_path_full.split("/")[-1][:-4])

    
    # array2raster output datatype
    datatype = 'int32'
    

    
    # common parameters
    noDataValue = -17.3


    SaveLayerDict = {}
    

    rasterOrigin, extent, SaveLayerDict_, NUTS3_name_dict = _cut_pop_layer_get_layer_origin(strd_raster_path_full, strd_raster_path
                                    , strd_vector_path, datatype)
    
    
    for k in SaveLayerDict_.keys():
        LL = SaveLayerDict_[k]
        a2r.array2raster(LL[0], LL[1], LL[2], LL[3], LL[4], LL[5] , LL[6])
        del LL
        #SaveLayerDict[k] = SaveLayerDict_[k]
        del SaveLayerDict_[k]
        
    cols = (extent[1]-extent[0])/100
    rows = (extent[3]-extent[2])/100
    RESULTS =  np.zeros((rows, cols), dtype="f4")
    if True:
        # takes vector layer (vectors are squares (1x1km - same size as population raster layer))
        # Information stored in Pop_Nuts.shape: NUmber of population per 1km and corresponding NUTS3 region
        # and Population per Nuts region (vector layer), same as the one two lines above
        # Population of corresponding NUTS 3 REGION to each 1x1km feature 
        print("\nProcess 5")
        st0 = time.time()
        count = 0
        #print ( country_file_list)
        #print ( country_file_list[1:10])
        #country_file_list = cfl
        for OSM_building_file in sorted(country_file_list):
            CONTINUE = False
            for ele in COUNTRIES:
                full_name = ele[2].lower()
                if full_name not in OSM_building_file.lower():
                    continue
                else:
                    CCode = ele[1]
                    if CCode not in NUTS3_name_dict.keys():
                        CONTINUE = True
                    else:
                        CONTINUE = False
                    break
            EXPORT_LAYERS = False
            count += 1
            
            if OSM_building_file == country_file_list[-1]:
                EXPORT_LAYERS = True
                
            if "austr" not in OSM_building_file:
                #continue    
                pass
            if count > 5000:
                pass
                #break
                         
            if CONTINUE == False or 1==1:
                
                
                country_name = "%s_%s" %(("000%i" %count)[-4:], OSM_building_file.split("/")[-2])
                country_file_name = "%s/%s.tif" %(proc_data_path, country_name)
                country_file_name_csv = "%s/%s" %(proc_data_path_csv, country_name)
                st = time.time()
                
                
                print("COUNT: %i  \n    -->  %s" %(count, OSM_building_file))
                SaveLayerDict_, BUILDNAME_DICT = _process5(org_data_path, OSM_building_file
                                           , temp_path, extent, strd_raster_path
                                           , country_file_name, noDataValue, BUILDNAME_DICT)
    
                if len(SaveLayerDict.keys()) >= 5:
                    EXPORT_LAYERS = True
                #"""
                
                
                
                        
                noDataValue = 0
                for k in sorted(SaveLayerDict_.keys()):
                    LL = SaveLayerDict_[k]
                    #print (k)
                    print ("Total Area %s - %s: %5.3f" % (country_name, k, np.sum(LL[5]))) 
                    
                    if 1==1:
                        st1 = time.time()
                        start_ele = 0 
                        print ("Number of Features: %i" % len(BUILDNAME_DICT))
                        for j in range(25):
                            if start_ele >= len(BUILDNAME_DICT):
                                break
                            with open(country_file_name_csv + "_build_names_%i.csv" %j, "w") as text_file:
                                for key1 in range(start_ele, len(BUILDNAME_DICT)):
                                    LE = BUILDNAME_DICT[key1]
                                    if LE[4] is None:
                                        key1_ = "None"
                                    else:
                                        key1_ = LE[4].replace(",", ";")
                                    text_file.write("%s,%s,%s,%s,%s,%f,%f,%f,%f\n" % (str(LE[0]), str(LE[1]), LE[2], str(LE[3]), 
                                                                                   key1_, LE[5], LE[6], LE[7], LE[8]))
                                    if key1 - 500000 >  start_ele:
                                        break
                                start_ele = key1 + 1
                        BUILDNAME_DICT = []
                        print (time.time() - st1)
                        print ("  CSV Export Done")
                        print ("Export %s" %k)
                        
                    if k == "data_r5" and EXPORT_LAYERS == True and 0==1:
                        
                        
                        stx = time.time()
                        
                        #print(LL[5].shape)
                        
                        #a2r.array2raster(country_file_name, LL[1], LL[2], LL[3]
                        #                 ,"uint32", LL[5] , noDataValue)
                        
                        # Replace Matrix by Path
                        SaveLayerDict_[k] = (country_file_name, LL[1], LL[2], LL[3]
                                             , LL[4]
                                             , country_file_name , -17.845213) 
                        print (time.time() -stx)
                    SaveLayerDict[country_name] = SaveLayerDict_[k]
                    del SaveLayerDict_[k]
                print("Number of Files Processed: %i" % len(SaveLayerDict.keys()))
                print(sorted(SaveLayerDict.keys()))
                #"""
                elapsed_time = time.time() - st
                print (elapsed_time)
               
            if EXPORT_LAYERS == True:
                print ("Export Layer")
                st1 = time.time()
                for k in sorted(SaveLayerDict.keys()):
                    LL = SaveLayerDict[k]
                    print("Process: %s" % LL[0])
                    
                    RESULTS = np.maximum(RESULTS, LL[5] / 10 ** 3) 
                
                
                    del SaveLayerDict[k]
                print ("Start Export")
                a2r.array2raster(LL[0], LL[1], LL[2], LL[3]
                                 , "float64", RESULTS , -17.845213)
                
                #a2r.array2raster(LL[0], LL[1], LL[2], LL[3]
                #                 , "float64", LL[5] , -17.845213)
                print ("Export Building Names: %i" % len(BUILDNAME_DICT))
                print (time.time() - st1)

                print ("  Export Done")
                print (time.time() - st1)
    
    
    
        #print("Process 5 took: %4.1f seconds" %(time.time() - st0))
    print ("Total Area: %5.3f" % np.sum(RESULTS))
    output = "%s/FINAL_AREA_OSM.tif" % proc_data_path                  
    print ("Outputfile: %s" % output)
    
    print ("Export Layers:")
    st = time.time()
    for k in sorted(SaveLayerDict.keys()):
        st1 = time.time()
        LL = SaveLayerDict[k]
        print("Process: %s" % LL[0])
                    
        RESULTS = np.maximum(RESULTS, LL[5]  / 10 ** 3)
        
        del SaveLayerDict[k]
        print (time.time() - st1)
    a2r.array2raster(output, LL[1], LL[2], LL[3], "float64", RESULTS , -17.845213)
    #print (time.time() - st)
    #st = time.time()
    print ("Export Building Names: %i" % len(BUILDNAME_DICT))
    """
    with open(output[:-4] + "_build_names.csv", "w") as text_file:
        for key1 in BUILDNAME_DICT.keys():
            if key1 is None:
                key1_ = "None"
            else:
                key1_ = key1.replace(",", ";")
            text_file.write("%s,%f,%f,%f\n" % (key1_, BUILDNAME_DICT[key1][0]
                                                       , BUILDNAME_DICT[key1][1]
                                                       , BUILDNAME_DICT[key1][2]))
                                """
    print("Process Export Layers took: %4.1f seconds" %(time.time() - st))  
    print("Total Process took: %4.1f seconds" %(time.time() - st0))    
    print("Done!!")
       
if __name__ == "__main__":
    
    main_process()