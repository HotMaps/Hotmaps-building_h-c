'''
Created on Jul 28, 2017

@author: simulant
'''

import gdal
import ogr
import os




def clip_raster_layer_vctr_feat(InputRasterFile, OutputRasterFile
                    , InputVectorFile, Vct_feat_id_LIST
                    , Vctr_key_field, datatype='int32'):
    """
    Clips raster file rectangular shape, 
    to the extent of a set given features of vector shape file
    Input
    InputRasterFile: Filename of Input raster
    OutputRasterFile: Filename of clipped raster file 
    InputVectorFile: Filename of vector input layer file
    Vct_feat_id_LIST: List of features of InputVectorFile to consider 
    Vctr_key_field: Key field of features
    datatype: Datatype of returned raster file
    
    returns:
    
    SaveLayerDict: Key: filename of output raster file (OutputRasterFile)
                List: [outRastPath, rasterOrigin2, pxWidth
                , pxHeight, DatType, arr_pop_cut , noDataVal]
    
    rasterOrigin
    extent
    
    """
    SaveLayerDict = {}
    if InputRasterFile != OutputRasterFile:
        
        #Get extent of selected features of shape file
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
        
        # Cut raster layer
        (outRastPath, rasterOrigin2, pxWidth, pxHeight, DatType, arr_pop_cut 
         , noDataVal_) = _clip_raster_layer(
                         InputRasterFile
                         , OutputRasterFile
                         , datatype
                         , fminx, fminy
                         , fmaxx, fmaxy)
        
        
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
        
        #Load (cutted) raster layer         
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


def _clip_raster_layer(InputRasterFile
                         , OutputRasterFile
                         , datatype
                         , fminx, fminy
                         , fmaxx, fmaxy):

    ########################################
    # Load Raster layer file
    # Cut with boundaries fminx,..fmaxy
    # Return cutted Raster layer image
    ######################################
    cutRastDatasource = gdal.Open(InputRasterFile)
    transform = cutRastDatasource.GetGeoTransform()
    minx = transform[0]
    maxy = transform[3]

    
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

    return (OutputRasterFile, rasterOrigin2, 1000, -1000
            , datatype, arr_out , 0)