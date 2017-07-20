import gdal, ogr, os, time, osr
import numpy as np



#@profile
def rasterize(inRasterPath, inVectorPath, fieldName, dataType, outRasterPath, noDataValue, RESOLUTION = 1000, FIELD_FILTER=None, BUILDNAME_DICT= None):
    
    
    """
    # Define pixel_size and NoData value of new raster
    pixel_size = 100
    NoData_value = -9999
    
    # Filename of input OGR file
    vector_fn = inVectorPath
    
    # Filename of the raster Tiff that will be created
    raster_fn = outRasterPath
    
    # Open the data source and read in the extent
    source_ds = ogr.Open(vector_fn)
    source_layer = source_ds.GetLayer()
    #source_layer.SetAttributeFilter("code = 1500")
    
    x_min, x_max, y_min, y_max = source_layer.GetExtent()
    
    # Create the destination data source
    x_res = int((x_max - x_min) / pixel_size)
    y_res = int((y_max - y_min) / pixel_size)
    
    target_ds = gdal.GetDriverByName('GTiff').Create(raster_fn, x_res, y_res, 1, gdal.GDT_Float32)
    target_ds.SetGeoTransform((x_min, pixel_size, 0, y_max, 0, -pixel_size))
    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromEPSG(3035)
    target_ds.SetProjection(outRasterSRS.ExportToWkt())
    
    band = target_ds.GetRasterBand(1)
    band.SetNoDataValue(NoData_value)

    # Rasterize
    gdal.RasterizeLayer(target_ds, [1], source_layer, burn_values=[0], options=["ATTRIBUTE=%s" %"code"])
    
    ####################################
    
    
    #"""
    #raise()
    
    #'''
    print("rasterize")
    st0 = time.time()

    inRastDatasource = gdal.Open(inRasterPath)
    transform = inRastDatasource.GetGeoTransform()
    minx = transform[0]
    maxy = transform[3]
    #maxx = minx + transform[1] * inRastDatasource.RasterXSize
    #miny = maxy + transform[5] * inRastDatasource.RasterYSize
    rasterOrigin = (minx, maxy)
    b = inRastDatasource.GetRasterBand(1)
    arr = b.ReadAsArray()
    x_res = arr.shape[0]     # 4472
    y_res = arr.shape[1]     # 5559   
    inRastDatasource = None
    
    arr_out = np.zeros((x_res*10, y_res*10),dtype = dataType)
    x_vec_origin = rasterOrigin[0] + 500
    y_vec_origin = rasterOrigin[1] - 500
    inShapefile = inVectorPath
    inDriver = ogr.GetDriverByName("ESRI Shapefile")
    inDataSource = inDriver.Open(inShapefile, 0)
    inLayer = inDataSource.GetLayer()
    if fieldName == "__AREA__":
        GET_AREA = True
    else:
        GET_AREA = False
    numFeat = inLayer.GetFeatureCount()
    st1 = time.time()
    j = 0
    RESpkm = RESOLUTION / 100
    
    offset = np.floor(4*RESpkm)/RESpkm
    
    (r_, c_) = arr_out.shape
    
    feat_list = []
    
    for i in range(0, numFeat):
        #if i % 300000 == 0:
        #    print ("     %i out of %i (%2.1f) --> %4.1f sec"% (i, numFeat, (i+1)*100.0/ (1+numFeat), time.time() - st1))
        inFeature = inLayer.GetFeature(i)
        """
        if i > 100000:
            break
        #"""
        feat_list.append(inFeature)
        if i > 100000:
            pass
            #break
    i = 0
    for inFeature in feat_list:
        i =i+1
        if i % 300000 == 0:
            print ("     %i out of %i (%2.1f) --> %4.1f sec"% (i, numFeat, (i+1)*100.0/ (1+numFeat), time.time() - st1))
        #"""
        
        if GET_AREA == True:
            val_ = inFeature.geometry().Area()
            if val_ < 80:
                height = 1.5
                
            elif val_ > 300:
                height = 4
            else:
                height = ((val_ - 80) / 220 * 2.5 + 1.5)
            bgf = height * val_
            
            
            #"""
        else:
            val_ = inFeature.GetField(fieldName)
        
        if not(val_ is None):
            geom = inFeature.GetGeometryRef()
            (x, y) = geom.Centroid().GetPoints()[0]
            """
            cent = geom.Centroid()
            x = cent.GetX()
            y = cent.GetY()
            
            x = geom.Centroid().GetX()
            y = geom.Centroid().GetY()
            """
            x_index = round((x + 45 - x_vec_origin)/RESOLUTION) #Addiere 45m
            y_index = round((y_vec_origin - (y - 45))/RESOLUTION) #Addiere eine 
            
            if BUILDNAME_DICT != None:
                build_name = inFeature.GetField(3)
                if build_name is None:
                    build_name = ""
                """if build_name in BUILDNAME_DICT.keys():
                    BUILDNAME_DICT[build_name] = [BUILDNAME_DICT[build_name][0] + 1
                                                  , BUILDNAME_DICT[build_name][1] + val_
                                                  , BUILDNAME_DICT[build_name][2] + bgf]
                
                else:
                #"""
                BUILDNAME_DICT.append([inFeature.GetField(0), inFeature.GetField(1), inFeature.GetField(2), inFeature.GetField(4), build_name, val_, bgf
                                                    ,x, y   ])
            
            
            
            temp = bgf #val_

            r1 = RESpkm*y_index + offset
            c1 = RESpkm*x_index + offset
            r1e = r1 + RESpkm
            c1e = c1 + RESpkm
            
            if r1 <= r_ and c1 <= c_:
                if r1e > 0 and c1e > 0:
                    try:
                        arr_out[r1 :r1e, c1:c1e] += temp
                    except Exception as e:
                        print (e)

    return (outRasterPath, rasterOrigin, 100, -100, dataType, arr_out, noDataValue, BUILDNAME_DICT)
    #a2r.array2raster(outRasterPath, rasterOrigin, 100, -100, dataType, arr_out, noDataValue)

    
    

if __name__ == "__main__":
    start_time = time.time()
    
    prj_path = "/home/simulant/ag_lukas/personen/Mostafa/EnergyDensityII"
    temp_path            = prj_path  + os.sep + "Temp"
    data_path            = prj_path  + os.sep + "Data"
    noDataValue = 0    

    inRasterPath = data_path + os.sep + "Population.tif"
    inVectorPath = temp_path + os.sep + "temp2.shp"
    fieldName = "sum"
    dataType = "float32"
    outRasterPath = prj_path + os.sep + "sum_ss_1km.tif"
    rasterize(inRasterPath, inVectorPath, fieldName, dataType, outRasterPath, noDataValue)
    
    '''
    fieldName = "ESPON_TOTA"
    outRasterPath = prj_path + os.sep + "Dem_in_Nuts.tif"
    rasterize(inRasterPath, inVectorPath, fieldName, dataType, outRasterPath, noDataValue)

    '''
    elapsed_time = time.time() - start_time
    print(elapsed_time)
    