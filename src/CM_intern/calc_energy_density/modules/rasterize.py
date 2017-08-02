import gdal, ogr, os, time
import numpy as np
import CM_intern.common_modules.array2raster as a2r #array2raster

def rasterize(inRasterPath, inVectorPath, fieldName, dataType
              , outRasterPath, noDataValue, saveAsRaster=False
              , pixelWidth=100, pixelHeight=-100):
    
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
    
    for i in range(0, inLayer.GetFeatureCount()):
        inFeature = inLayer.GetFeature(i)
        #if x_index<x_res*10 and y_index<y_res*10:
        value_ = inFeature.GetField(fieldName)
        
        if not(value_ is None):
            geom = inFeature.GetGeometryRef().Centroid()
            
            x = geom.GetX()
            y = geom.GetY()
            #         if x>x_vec_origin and y>y_vec_origin :
            x_index = round((x - x_vec_origin)/1000)
            y_index = round((y_vec_origin - y)/1000)
            #temp = inFeature.GetField(fieldName)
            
            arr_out[10*y_index:10*y_index+10, 10*x_index:10*x_index+10] = value_
    inFeature = None   
    # rev_array = arr_out[::-1] # reverse array so the tif looks like the array
    if saveAsRaster == True:
        a2r.array2rasterfile(outRasterPath, rasterOrigin, pixelWidth
                         , pixelHeight, dataType
                         , arr_out, noDataValue) # convert array to raster
        
    return (outRasterPath, rasterOrigin, pixelWidth
                         , pixelHeight, dataType
                         , arr_out, noDataValue)


    

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
    