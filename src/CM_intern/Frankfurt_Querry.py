import numpy as np
import pandas as pd
import gdal
import osr
import time

def array2raster(outRasterPath, rasterOrigin, pixelWidth, pixelHeight, dataType, array, noDataValue):
    # conversion of data types from numpy to gdal
    dict_varTyp = {
                   "int8":      gdal.GDT_Byte,
                   "int16":     gdal.GDT_Int16,
                   "int32":     gdal.GDT_Int32,
                   "uint16":    gdal.GDT_UInt16,
                   "uint32":    gdal.GDT_UInt32,
                   "float32":   gdal.GDT_Float32,
                   "float64":   gdal.GDT_Float64
                   }
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


def zonStat_dem_frankfurt(inputCSV, outRasterPath):
    # population raster origin: to define a fishnet that matches to default data set
    # the origin of population raster is required. This is treated as a standard 
    # origin of the fish net with 100m resolution. This refers to the top-left corner
    # of the raster. The following value is given in EPSG:3035
#     fishnet_orig = (944000,5414000)
#     x0 = fishnet_orig[0]
#     y0 = fishnet_orig[1]
    ifile = pd.read_csv(inputCSV)
    demand = ifile['Demand'].values
    X = ifile['X'].values
    Y = ifile['Y'].values
    
    x0 = 100 * np.floor(np.min(X)/100).astype(int)
    y0 = 100 * np.ceil(np.max(Y)/100).astype(int)
    rasterOrigin = (x0, y0)
    
    xIndex = np.floor((X-x0)/100.0).astype(int)
    yIndex = np.floor((y0-Y)/100.0).astype(int)
#     rasterXorigin = x0 + 100 * np.min(xIndex)
#     rasterYorigin = y0 - 100 * np.min(yIndex)
#     rasterOrigin = (rasterXorigin, rasterYorigin)
    xWidth = np.max(xIndex) - np.min(xIndex) + 1
    yWidth = np.max(yIndex) - np.min(yIndex) + 1
    index = xIndex + xWidth * yIndex 
    sortedData = np.asarray(sorted(zip(index, demand),key=lambda x:x[0]))
    unique, counts = np.unique(index, return_counts=True)
    end = np.cumsum(counts)
    st = np.concatenate((np.zeros((1)), end[0:end.size-1]))
    # xIndex and yIndex start from 0. So they should be added by 1
    sumDem = np.zeros((np.max(xIndex)+1)*(np.max(yIndex)+1))
    
    item_location = 0
    for item in unique:
        # sum of demand for each index
        startIndex = int(st[item_location])
        endIndex = int(end[item_location])
        sumDem[item] = np.sum(sortedData[startIndex:endIndex,1])
        item_location += 1
    # xWidth and yWidth in the following refer to columns and rows, respectively and
    # should not wrongly be considered as coordination!
    sumDem = sumDem.reshape((yWidth,xWidth))
    array2raster(outRasterPath, rasterOrigin, 100, -100, "float32", sumDem, 0)
    
def Frankfurt_Querry(inputCSV1,inputCSV2,inputCSV3,outputCSV):

    # Building demand based on type [GWh/m2/a]
    # Frankfurt has no data regarding age of the building. In case such data exist
    # it should be considered in calculation.
    # demand types: 0: no demand; 1: einzelhaus; 2: Doppelhaus, 3: Reihenhaus; 4: Mehrfamilienhaus; 5:Mischnutzung; 6: Buero
    # 7: Gewerbe; 8 Beherbergung; 9: Gastronomie; 10:oeffentliches Gebaeude; 11: Schule; 12: Krankenhaus; 13: Schwimmbad
    demand_typ = np.array([0, 219, 212, 205, 134, 189, 177, 220, 269, 253, 144, 157, 311, 311]) * 0.000001
    # Building types based on the category provided in the shapefile. This 
    # category is used for those entries that do not exist in the Access database.
    dict_typ_conv = {
             "1000.0":1,"1020.0":4,"1022.0":4,"1100.0":3,"1120.0":3,"1223.0":4,
             "2010.0":3,"2020.0":3,"2030.0":5,"2040.0":3,"2051.0":3,"2052.0":3,
             "2053.0":3,"2055.0":3,"2056.0":3,"2060.0":5,"2070.0":4,"2071.0":4,
             "2074.0":4,"2081.0":4,"2090.0":5,"2092.0":5,"2100.0":3,"2130.0":0,
             "2320.0":3,"2410.0":3,"2420.0":3,"2430.0":3,"2431.0":3,"2443.0":3,
             "2460.0":0,"2461.0":0,"2462.0":0,"2463.0":0,"2465.0":0,"2501.0":0,
             "2510.0":3,"2511.0":3,"2513.0":0,"2520.0":0,"2522.0":0,"2523.0":0,
             "2540.0":3,"2570.0":0,"2580.0":3,"2620.0":0,"2700.0":3,"2721.0":0,
             "2723.0":0,"2740.0":3,"3010.0":3,"3012.0":5,"3013.0":5,"3014.0":5,
             "3015.0":5,"3016.0":5,"3020.0":5,"3021.0":5,"3022.0":5,"3023.0":5,
             "3024.0":5,"3030.0":5,"3031.0":5,"3032.0":5,"3033.0":5,"3034.0":5,
             "3035.0":3,"3036.0":5,"3037.0":5,"3040.0":5,"3041.0":5,"3042.0":5,
             "3044.0":5,"3045.0":5,"3046.0":5,"3047.0":5,"3048.0":5,"3050.0":6,
             "3051.0":6,"3052.0":6,"3060.0":5,"3061.0":4,"3062.0":4,"3065.0":5,
             "3070.0":5,"3071.0":3,"3072.0":3,"3073.0":4,"3074.0":0,"3075.0":4,
             "3080.0":0,"3081.0":5,"3082.0":0,"3091.0":5,"3092.0":5,"3094.0":5,
             "3095.0":5,"3097.0":3,"3211.0":5,"3221.0":7,"3222.0":7,"3230.0":3,
             "3260.0":3,"3270.0":3,"3290.0":5,"11491.0":4,"13074.0":0,"19950.0":0,
             "19951.0":0,"19952.0":0,"19953.0":5
            }
    
    # The input files 1 and 2 are read as string because the following process 
    # is valid only with this data ty-pe.
    
    ########## read file 1
    ifile1 = pd.read_csv(inputCSV1).astype('str')
    ifile1 = ifile1.sort_values(["Strvrz","HausNr"])
    ID = ifile1['ID'].values.astype(int)
    KGF = ifile1['KGF'].values.tolist()
    Strvrz1 = ifile1['Strvrz'].values
    HausNr1 = ifile1['HausNr'].values
    nRows1 = len(ID)
    GArt1 = np.zeros(nRows1) - 1
    ########## read file 2
    ifile2 = pd.read_csv(inputCSV2).astype('str')
    ifile2 = ifile2.sort_values(["STRASSENKENNZIFFER","HAUSNUMMER"])
    Strvrz2 = ifile2['STRASSENKENNZIFFER'].values
    HausNr2 = ifile2['HAUSNUMMER'].values
    GArt2 = ifile2['GEBAEUDEART'].values   
    
    ###########################################################################
    ###########################################################################
    # In addition to "Strvrz1 + ' ' + HausNr1", the post code (PLZ) must also 
    # be considered both in sorting process above and also in the following 
    # process. This is for the cases that two similar addresses with different
    # PLZ exist.
    # However, since the Frankfurt shapefile does not include PLZ values, it is
    # neglected here.
    ###########################################################################
    # note that a[st:end] referes to elements of a including "st" and excluding end.
    # Note: To get the last element of the same type, however, cumsum shoud be subtracted by 1:
    # (e.g. [1,1,1,1,2,2,2]: hear st for 1 is 0; end for 1 is 4; the last element which is one is 3)
    ###########################################################################
    ###########################################################################
    uniques1, counts1 = np.unique(Strvrz1 + ' ' + HausNr1, return_counts = True)
    uniques2, counts2 = np.unique(Strvrz2 + ' ' + HausNr2, return_counts = True)
    end1 = np.cumsum(counts1.astype(int))
    end2 = np.cumsum(counts2.astype(int))
    length = end1.size
    st1 = np.concatenate((np.zeros((1)), end1[0:length-1]))
    for i in range(length):
        # perform lookup to find building type from Access database. Lookup
        # returns an array of size greater or equal 0. 
        lookup = np.argwhere(uniques2 ==uniques1[i])
        # in the following, we get the last item (end) with similar value of a 
        # series.
        lookupVal = GArt2[end2[lookup]-1]
        if lookupVal.size>0:
            GArt1[int(st1[i]):int(end1[i])] = lookupVal[0].astype(int)
    
    # seperate IDs that do not exist in Access. Also remove repeated IDs.
    shortListID = ID[GArt1 != -1].astype(int)
    shortListGArt = GArt1[GArt1 != -1].astype(int)
    # stack_ is in form of [[IDs ....],
    #                       [Garts ..]]
    stack_ = np.vstack((shortListID, shortListGArt))
    extraID = ID[GArt1 == -1]
    # Since the loopup process was performed based on addresses and NOT IDs,
    # through the following process, addresses with IDs to which a building type
    # was assigned should be taken out i.e. for the cases that three address have
    # one ID and a building type was assigned only to one of them.
    # This is done with performing a difference on set.
    DifID = np.setdiff1d(extraID, shortListID).astype(int)
    # Assigne building type from dictionary
    for id in DifID:
        k = int(np.argwhere(ID == id)[0])
        temp = np.array([[id],[dict_typ_conv[KGF[k]]]])
        stack_ = np.concatenate((stack_,temp),axis=1)
    # sort the stack_ array based on IDs and then remove repeated items        
    stack_ = stack_[:,stack_[0,:].argsort()]
    uniStack, stackCounts = np.unique(stack_[0], return_counts = True)
    # To include all elements of stack_ in stack_f, the starting values of sorted stack_ can be used:
    stackend = np.cumsum(stackCounts)
    stackst =  np.concatenate((np.zeros((1)), stackend[0:stackend.size-1]))
    stack_f = stack_[:,stackst.astype(int)]

    ########## read file 3
    # open shapefile list and assign building types to the entries based on Access categories
    ifile3 = pd.read_csv(inputCSV3)
    ID = ifile3['ID'].values
    SDG = ifile3['SDG'].values.tolist()
    KGF = ifile3['KGF'].values.tolist()
    OBJ = ifile3['OBJ'].values.tolist()
    NFA = ifile3['NFA'].values
    NrFloor = ifile3['NrFloor'].values
    GFA = ifile3['GFA'].values
    X = ifile3['X'].values.tolist()
    Y = ifile3['Y'].values.tolist()
    GArt = np.zeros(len(ID))
    # ID starts from 1. Therefore, here is should be subtracted by one
    GArt = stack_f[1,ID.astype(int)-1]
    demand = np.zeros_like(GArt)
    demand = demand_typ[GArt]* GFA
    GArt = GArt.tolist()
    demand = demand.tolist()
    
    ########## save the result to csv file
    d = {"ID": ID, "NFA": NFA, "NrFloor": NrFloor, "GFA": GFA, "KGF": KGF, "GArt": GArt, "SDG": SDG, "OBJ": OBJ, "Demand": demand, "X": X, "Y": Y}
    df = pd.DataFrame(d)
    col = ["ID", "SDG", "GArt", "KGF", "OBJ", "NFA", "NrFloor", "GFA", "Demand", "X", "Y"]
    df = df[col]
    df = df.sort_values(["ID","OBJ"])
    df.to_csv(outputCSV)
    
    
    
if __name__ == "__main__":
    start = time.time()
    inputCSV1 = "/home/simulant/ag_lukas/personen/Mostafa/Frankfurt Buildingblocks/Frankfurt_Data.csv"
    inputCSV2 = "/home/simulant/ag_lukas/personen/Mostafa/Frankfurt Buildingblocks/GEBAEUDE_Access.csv"
    inputCSV3 = "/home/simulant/ag_lukas/personen/Mostafa/Frankfurt Buildingblocks/Frankfurt_coords.csv"
    outputCSV = "/home/simulant/ag_lukas/personen/Mostafa/Frankfurt Buildingblocks/Frankfurt_Data_final.csv"
    outRasterPath = "/home/simulant/ag_lukas/personen/Mostafa/Frankfurt Buildingblocks/Frankfurt_ZS.tif"
    Frankfurt_Querry(inputCSV1,inputCSV2,inputCSV3,outputCSV)
    zonStat_dem_frankfurt(outputCSV, outRasterPath)
    print(time.time() - start)