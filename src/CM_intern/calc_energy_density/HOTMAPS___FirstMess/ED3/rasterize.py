import gdal, ogr, os, time, osr
import numpy as np


def rasterize(inRasterPath, inVectorPath, fieldName, dataType, outRasterPath, noDataValue, RESOLUTION = 1000, FIELD_FILTER=None):
    
    
    """
    # Define pixel_size and NoData value of new raster
    pixel_size = 20
    NoData_value = -9999
    
    # Filename of input OGR file
    vector_fn = inVectorPath
    
    # Filename of the raster Tiff that will be created
    raster_fn = '%s.tif' % outRasterPath
    
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
    """
    
    """
    #raise()
    
    """
    print("rasterize")
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
    for i in range(0, numFeat):
        if i % 300000 == 0:
            print ("     %i out of %i (%2.1f) --> %4.1f sec"% (i, numFeat, (i+1)*100.0/ (1+numFeat), time.time() - st1))
            j += 1
            if j > 2:
                pass
                #break
        inFeature = inLayer.GetFeature(i)
        #if x_index<x_res*10 and y_index<y_res*10:
        if GET_AREA == True:
            val_ = inFeature.geometry().Area()
        else:
            val_ = inFeature.GetField(fieldName)
        
        if not(val_ is None):
            geom = inFeature.GetGeometryRef()
            (x, y) = geom.Centroid().GetPoints()[0]
            #x = geom.Centroid().GetX()
            #y = geom.Centroid().GetY()
            #         if x>x_vec_origin and y>y_vec_origin :
            x_index = round((x + 45 - x_vec_origin)/RESOLUTION) #Addiere 45m
            y_index = round((y_vec_origin - (y - 45))/RESOLUTION) #Addiere eine 
            temp = val_ #inFeature.GetField(fieldName)
            """for m in range(10):
                for n in range(10):
                    arr_out[10*y_index+n, 10*x_index+m] = temp
            """
            r1 = RESpkm*y_index + offset
            c1 = RESpkm*x_index + offset
            
            if r1 <= r_ and c1 <= c_:
                r1e = r1 + RESpkm
                c1e = c1 + RESpkm
                if r1e > 0 and c1e > 0:
                    
                    try:
                        arr_out[r1 :r1e
                             , c1:c1e] += temp 
                    except Exception as e:
                        print (e)
    inFeature = None   
    
    
    
    
    # rev_array = arr_out[::-1] # reverse array so the tif looks like the array
    return (outRasterPath, rasterOrigin, 100, -100, dataType, arr_out, noDataValue)
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
    