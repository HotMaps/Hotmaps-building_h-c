'''
Created on Jul 28, 2017

@author: simulant
'''

import gdal
import ogr
import os



def clip_raster_layer(InputRasterFile, OutputRasterFile
                    , InputVectorFile, Vct_feat_id_LIST
                    , Vctr_key_field, datatype='int32'):
    
    SaveLayerDict = {}
    if InputRasterFile != OutputRasterFile:
        Vctr_key_field = "NUTS_ID"
        #feat_id_LIST = [12,13,14]  # 14refers to the feature ID of Vienna
        
        (outRastPath, rasterOrigin2, pxWidth, pxHeight, DatType, arr_pop_cut 
         , noDataVal_, feat_name_dict) = _clip_raster_layer(
                         InputVectorFile
                         , Vct_feat_id_LIST
                         , Vctr_key_field
                         , InputRasterFile
                         , OutputRasterFile
                         , datatype)
        
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
        cutRastDatasource = gdal.Open(OutputRasterFile)
        transform = cutRastDatasource.GetGeoTransform()
        RasterXSize = cutRastDatasource.RasterXSize
        RasterYSize = cutRastDatasource.RasterYSize
    
    minx = transform[0]
    maxy = transform[3]
    maxx = minx + transform[1] * RasterXSize
    miny = maxy + transform[5] * RasterYSize
    extent = (minx,maxx,miny,maxy)
    rasterOrigin = (minx, maxy)
    
    return SaveLayerDict, rasterOrigin, extent


def _clip_raster_layer(InputVectorFile
                         , Vct_feat_id_LIST
                         , Vctr_key_field
                         , InputRasterFile
                         , OutputRasterFile
                         , datatype):
        
        # Vector Layer with selected specific feature
        inDriver = ogr.GetDriverByName("ESRI Shapefile")
        #Assert file exists
        assert(os.path.exists(InputVectorFile))
        
        inDataSource = inDriver.Open(InputVectorFile, 0)
        inLayer = inDataSource.GetLayer()
        fminx = fminy = 10**10
        fmaxx = fmaxy = 0
        feat_name_dict = {}
        for feat_id in Vct_feat_id_LIST:
            try:
                inFeature = inLayer.GetFeature(feat_id)
                FeatName = (inFeature.GetField(Vctr_key_field))
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
        cutRastDatasource = gdal.Open(InputRasterFile)
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

        return (OutputRasterFile, rasterOrigin2, 1000, -1000, datatype, arr_out , 0, feat_name_dict)