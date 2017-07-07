'''
Created on Apr 20, 2017

@author: simulant
'''
import gdal, ogr, osr, time
import numpy as np
from skimage import morphology, measure
from skimage.morphology import binary_closing, binary_dilation, binary_erosion, square




def array2raster(outRasterPath,rasterOrigin,pixelWidth,pixelHeight,dataType,array,noDataValue):
    # conversion of data types from numpy to gdal
    dict_varTyp ={"int8" : gdal.GDT_Byte, "int16" : gdal.GDT_Int16, "int32" : gdal.GDT_Int32, "uint16" : gdal.GDT_UInt16, "uint32" : gdal.GDT_UInt32, "float32" : gdal.GDT_Float32, "float64" : gdal.GDT_Float64}
    cols = array.shape[1]
    rows = array.shape[0]
    originX = rasterOrigin[0]
    originY = rasterOrigin[1]

    driver = gdal.GetDriverByName('GTiff')
    outRaster = driver.Create(outRasterPath, cols, rows, 1, dict_varTyp[dataType], ['compress=LZW'])
    outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromEPSG(3035)
    outRaster.SetProjection(outRasterSRS.ExportToWkt())
    outRaster.GetRasterBand(1).SetNoDataValue(noDataValue)
    outRaster.GetRasterBand(1).WriteArray(array)
    outRaster.FlushCache()


 
def potDHAreas(DH,g,rasterOrigin,fid,pix_threshold,DH_threshold, minSizeObj=3,minSizeHole=5, conn=2):
    """
    Calculate potential district heating areas
    input:
        heat_density_map: numpy array created from heat density map containing demand in 1ha pixels
        threshold: minimum demand in each pixel which makes it potential part of DH area
        minSizeObj: minimum area to be covered by connected object justifying development of district heating.
        minSizeHole: removes the holes smaller than this size
        bridge: square(2): The neighborhood expressed as a 2-D array of 1's and 0's. In our problem, "square(2)" refers to 100m distance.  
        conn: The connectivity defining the neighborhood of a pixel. it should be set to "2" to consider diagonal connectivities (DO NOT CHANGE IT UNLESS for a good reason).
        
    Output:
        DH: a boolean 2-D array with elements of "1" for potential district heating areas with the same resolution of the input "heat_density_map"
    
    
    """
    
#     ds1 = gdal.Open(heat_density_map)
#     b1 = ds1.GetRasterBand(1)
#     arr1 = b1.ReadAsArray().astype('float32')
#     arr1=heat_density_map
    
#     transform = ds1.GetGeoTransform()
#     minx = transform[0]
#     maxy = transform[3]
#     rasterOrigin = (minx, maxy)
    
#     print(1)
#     
#     g = arr1*(arr1>pix_threshold)
#     DH = arr1>pix_threshold
#     print(DH.dtype)
#     #ds1=arr1=None
#     
#     print(2)
    # removes connected objects that are smaller than "minSizeObj". also the connected Null objects within non-zero connected object are removed if they have a size of "smaller" than "minSizeHole"
    # blobs1 = morphology.remove_small_objects(DH, min_size=minSizeObj, connectivity=conn)
    # blobs  = morphology.remove_small_holes(blobs1, min_size=minSizeHole).astype(int)
    #blobs = blobs1.astype(int)
    blobs = DH.astype(int)
    #print(3)
    
    
#    all_labels = measure.label(blobs)
#################################################################################################################################################################################
#   important note: the value of "1" is added to blobs_labels becouse in the existing version of python in server 155 the background values are returned as "-1". However, in Anaconda, the background elements are 0.
#                   in case this changed, consider relevant change in "for" loop in the foloowings. 
#################################################################################################################################################################################
    blobs_labels1 = measure.label(blobs, background=0)
    if blobs_labels1.size>0:
        numLabels = np.amax(blobs_labels1)
    
    
        #print(numLabels)
        
        unique, counts = np.unique(blobs_labels1, return_counts=True)
        dict_ = dict(zip(unique, counts))
        
        test = np.zeros(numLabels+1)
        
        
        for i in range(1,numLabels+1):
            if dict_[i]>100:
                test[i]=1
            
    #         if dict_[i]<100:
    #             dict_[i]=0
    #         else:
    #             dict_[i]=i
    
        blobs_labels1 = test[blobs_labels1]
        
    
        #print("yes")
        
        blobs_labels = measure.label(blobs_labels1, background=0)
        numLabels = np.amax(blobs_labels)
        
        
        #print(numLabels)
        
        #raise()
        '''
        k1=np.array(())
        k2=np.array(())
        for i in range(numLabels+1):
            t=np.where(blobs_labels==i)
            m=np.sum(g[t])
        
            #m = g * (blobs_labels==i)
            #if np.sum(m) < DH_threshold:
            if m < DH_threshold:
                k1=np.concatenate((k1, t[0]))
                k2=np.concatenate((k1, t[1]))
                
        '''        
        
        
        #print(blobs_labels.dtype)        
        ttt=blobs_labels>0
        g= g*ttt
        
        
        #print(5)
        
        DH=ttt.astype(int)
        #g=g[blobs_labels.astype(bool)]
        
        ################################################################################################
        outRasterPath = "/home/simulant/ag_lukas/personen/Mostafa/potDH/"+str(fid)+".tif"
        array2raster(outRasterPath,rasterOrigin,100,-100,"int8",DH,0)
    



def NutsCut(heat_density_map, strd_vector_path):
#         key_field = "NUTS_ID"
#         feat_id_LIST = [14,15,13]  # 14refers to the feature ID of Vienna
#         #feat_id_LIST = [14]  # 14refers to the feature ID of Vienna
#         feat_id_LIST = range(1290,1300)  # 14refers to the feature ID of Vienna
#         # Load NUTS3 Layer select specific feature (certain Nuts3 region)
########################################
    # Load population layer
    # Cut with boundaries defined by Shape of NUSTS 3 Layer
    # Save smaller population layer image
    ######################################
    
    pix_threshold = 0.1
    
    
    
    
    cutRastDatasource = gdal.Open(heat_density_map)
    transform = cutRastDatasource.GetGeoTransform()
    minx = transform[0]
    maxy = transform[3]
#         maxx = minx + transform[1] * cutRastDatasource.RasterXSize
#         miny = maxy + transform[5] * cutRastDatasource.RasterYSize
#         rasterOrigin = (minx, maxy)
    b11 = cutRastDatasource.GetRasterBand(1)
    arr1 = b11.ReadAsArray().astype(float)
    
    
    g = arr1*(arr1>pix_threshold)
    DH = arr1>pix_threshold
    (dimX,dimY) = DH.shape
    
    
    

    inDriver = ogr.GetDriverByName("ESRI Shapefile")
    inDataSource = inDriver.Open(strd_vector_path, 0)
    inLayer = inDataSource.GetLayer()
    fminx = fminy = 10**10
    fmaxx = fmaxy = 0
    flag = 0
    
    for fid in range(inLayer.GetFeatureCount()):
        print(fid)
        fminx = fminy = 10**10
        fmaxx = fmaxy = 0
    
        inFeature = inLayer.GetFeature(fid)
        
        geom = inFeature.GetGeometryRef()
        #Get boundaries
        fminx_, fmaxx_, fminy_, fmaxy_ = geom.GetEnvelope()
        fminx = min(fminx_, fminx)
        fminy = min(fminy_, fminy)
        fmaxx = max(fmaxx_, fmaxx)
        fmaxy = max(fmaxy_, fmaxy)        
        
        
        # define exact index that encompasses the feature.
        lowIndexY=int((fminx-minx)/100.0)
        lowIndexX=int((maxy-fmaxy)/100.0)
        upIndexY=lowIndexY+int((fmaxx-fminx)/100.0)
        upIndexX=lowIndexX+int((fmaxy-fminy)/100.0)
        while minx + upIndexY*100 < fmaxx:
            upIndexY = upIndexY + 1
        while maxy - upIndexX*100 > fminy:
            upIndexX = upIndexX + 1
        
        
        if lowIndexY<0:
            lowIndexY = 0
            flag = 1
        if lowIndexX<0:
            lowIndexX = 0
            flag = 1
        if upIndexY>dimY:
            upIndexY = dimY
            flag = 1
        if upIndexX>dimX:
            upIndexX = dimX
            flag = 1
        
        if flag ==1:
            print("feature '%s' is out of range of the input heat density map" %str(fid))
            flag = 0
        
            
        
        # considering the 1km resolution of strd raster, the raster origin should be a factor of 1000. this will be done in the following code.
        rasterOrigin2 = (minx + lowIndexY*100,maxy - lowIndexX*100)
        
        arr_out1= DH[lowIndexX:upIndexX,lowIndexY:upIndexY]
        arr_out2= g[lowIndexX:upIndexX,lowIndexY:upIndexY]
        
        potDHAreas(arr_out1,arr_out2,rasterOrigin2,fid,0.1,10)
        arr_out1 = None
        arr_out2 = None
        inFeature = None
        
        
        
        
        
        
        
        
        
        
        
        
    cutRastDatasource = None
    arr1 = None
    ########################################
    # END
    #
    ######################################







if __name__ == "__main__":
    start=time.time()
    #heat_density_map = "/home/simulant/ag_lukas/personen/Mostafa/DHpot/Au.tif"
    heat_density_map = "/home/simulant/ag_lukas/personen/Mostafa/DHpot/demand_v2_complete.tif"
    strd_vector_path = "/home/simulant/ag_lukas/personen/Mostafa/DHpot/NUTS3.shp"
    
    NutsCut(heat_density_map, strd_vector_path)
    #potDHAreas(heat_density_map,0.8,10, 4,5)
    elapsed=time.time()-start
    print(elapsed)
    