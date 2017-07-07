'''
Created on May 5, 2017

@author: Mostafa
'''
import gdal, ogr, osr, time
import numpy as np
from scipy import ndimage
from scipy.ndimage import measurements,binary_fill_holes
#from skimage import morphology, measure
#from skimage.morphology import binary_closing, binary_dilation, binary_erosion, square

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

 
#def potDHAreas(DH,rasterOrigin,fid,pix_threshold,DH_threshold, minSizeObj=3,minSizeHole=5, conn=2):
def DHRegions(DH,DH_threshold):
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
    ####################################################################################
    # removes connected objects that are smaller than "minSizeObj". also the connected Null objects within non-zero connected object are removed if they have a size of "smaller" than "minSizeHole"
    # blobs  = morphology.remove_small_holes(blobs1, min_size=minSizeHole).astype(int)
    ####################################################################################
    
    DH_noHole = binary_fill_holes(DH)
    
    # "struct" defines how the connected components can be considered.
    struct = np.ones((3,3)).astype(int)
    labels , numLabels = measurements.label(DH_noHole,structure=struct)
    
    if labels.size>0:
        #labels start from 1. Therefore, PotDH should have numLabels+1 elements
        PotDH = np.zeros((numLabels+1)).astype(bool)
        sparseRow,sparseCol = np.nonzero(labels)
        sparseLabels = labels[sparseRow , sparseCol] #this helps to implement "np.unique" much faster
        sparseDH = DH[sparseRow , sparseCol]
        # sort sparse values based on sparseLabels. This helps to implement summation process much faster.
        sortedSparseData = np.asarray(sorted(zip(sparseRow,sparseCol,sparseLabels,sparseDH),key=lambda x:x[2]))
        unique, counts = np.unique(sparseLabels, return_counts=True)
        end = np.cumsum(counts)
        st = np.concatenate((np.zeros((1)), end[0:numLabels-1]+1))
        # "dict_" might be usefull when you need to apply area constraint for a DH region.
        # dict_ = dict(zip(unique, counts))

        for i in range(numLabels):
            # sum over sparseDH
            pot = np.sum(sortedSparseData[st[i]:end[i],3])
            if pot>=DH_threshold:
                # here should be i+1 because labeling starts from one and not from zero
                PotDH[i+1] = True
        
        '''
        # With this loop you can add another criterion for the minimum area required to consider a region as DH region.
        for i in range(1,numLabels+1):
            if dict_[i]>100:
                test[i]=1
            
            if dict_[i]<100:
                dict_[i]=0
            else:
                dict_[i]=i
        '''
        DH_regions = PotDH[labels]
        return DH_regions
        ################################################################################################

def DHPotential(DH_Regions,HD):
    print("Calculate DH potentials")
    struct = np.ones((3,3)).astype(int)
    labels , numLabels = measurements.label(DH_Regions,structure=struct)
    unique = np.arange(numLabels+1)
    DHPot = ndimage.sum(HD,labels,unique)
    DH_Potential = DHPot[labels]
    return DH_Potential

def NutsCut(heat_density_map, strd_vector_path, pix_threshold, DH_threshold, outRasterPath):
    
    cutRastDatasource = gdal.Open(heat_density_map)
    transform = cutRastDatasource.GetGeoTransform()
    minx = transform[0]
    maxy = transform[3]
    rasterOrigin = (minx, maxy)
    b11 = cutRastDatasource.GetRasterBand(1)
    arr1 = b11.ReadAsArray().astype(float)
    
    DH = arr1*(arr1>pix_threshold)
    (dimX,dimY) = DH.shape
    DH_Regions = np.zeros((dimX,dimY)).astype(bool)

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
        
        # check if input shapefile exceed the boundaries of input raster file.
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

        # rasterOrigin2 = (minx + lowIndexY*100,maxy - lowIndexX*100)
        
        arr_out= DH[lowIndexX:upIndexX,lowIndexY:upIndexY]
        DH_Selected_Region = DHRegions(arr_out, DH_threshold)
        DH_Regions[lowIndexX:upIndexX,lowIndexY:upIndexY] += DH_Selected_Region
        arr_out = None
        inFeature = None
    
    result = DHPotential(DH_Regions,arr1)
    array2raster(outRasterPath,rasterOrigin,100,-100,"float32",result,0)
   
    cutRastDatasource = None
    arr1 = None





if __name__ == "__main__":
    start=time.time()
    #heat_density_map = "/home/simulant/ag_lukas/personen/Mostafa/DHpot/Au.tif"
    heat_density_map = "/home/simulant/ag_lukas/personen/Mostafa/DHpot/demand_v2_complete.tif"
    #strd_vector_path = "/home/simulant/ag_lukas/personen/Mostafa/DHpot/NUTS3.shp"
    strd_vector_path = "/home/simulant/ag_lukas/personen/Mostafa/DHpot/EU28.shp"
    outRasterPath = "/home/simulant/ag_lukas/personen/Mostafa/potDH/Pot_EU28_TH10.tif"
    pix_threshold = 0.1
    DH_threshold = 10
    NutsCut(heat_density_map, strd_vector_path, pix_threshold, DH_threshold, outRasterPath)
    elapsed=time.time()-start
    print(elapsed)
    