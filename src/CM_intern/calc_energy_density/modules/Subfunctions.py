import gdal, ogr
import os

'''
Created on Apr 23, 2017

@author: simulant
'''

def rrl(file_name, data_type="f4", raster_band=1):
    #read raster layer and return array
    return read_raster_layer(file_name, data_type, raster_band)
    
    

def read_raster_layer(file_name, data_type="f4", raster_band=1):
    #read raster layer and return array
    print("Reading: %s" % file_name)
    ds = gdal.Open(file_name)
    band = ds.GetRasterBand(raster_band)
    print ("   Got RasterBand")
    arr = band.ReadAsArray().astype(data_type)
    print ("   Done!")
    return  arr
    

def cut_population_layer(feat_id_LIST
                         , strd_vector_path
                         , strd_raster_path_full
                         , strd_raster_path
                         , datatype):
        key_field = "NUTS_ID"
        
        # Load NUTS3 Layer select specific feature (certain Nuts3 region)
        inDriver = ogr.GetDriverByName("ESRI Shapefile")
        #Assert file exists
        assert(os.path.exists(strd_vector_path))
        
        inDataSource = inDriver.Open(strd_vector_path, 0)
        inLayer = inDataSource.GetLayer()
        fminx = fminy = 10**10
        fmaxx = fmaxy = 0
        feat_name_dict = {}
        for feat_id in feat_id_LIST:
            try:
                inFeature = inLayer.GetFeature(feat_id)
                FeatName = (inFeature.GetField(key_field))
                print (FeatName)
                if FeatName[:2] in feat_name_dict.keys():
                    feat_name_dict[FeatName[:2]].append(FeatName)
                else:
                    feat_name_dict[FeatName[:2]] = [FeatName]
                geom = inFeature.GetGeometryRef()
                #Get boundaries
                fminx_, fmaxx_, fminy_, fmaxy_ = geom.GetEnvelope()
                fminx = min(fminx_, fminx)
                fminy = min(fminy_, fminy)
                fmaxx = max(fmaxx_, fmaxx)
                fmaxy = max(fmaxy_, fmaxy) 
                inFeature = None
            except:
                break
            
                   
        
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
        lowIndexY=max(0, int((fminx-minx)/1000.0))
        lowIndexX=max(0, int((maxy-fmaxy)/1000.0))
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

        return (strd_raster_path, rasterOrigin2, 1000, -1000, datatype, arr_out , 0, feat_name_dict)
        

    