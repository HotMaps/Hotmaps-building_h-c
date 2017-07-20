from osgeo import ogr, osr
import os
import time
import numpy as np
CREATE_MEM_LAYER = False
SET_SPATIAL_FILTE = True
VERBOSE = False
#@profile
def query(input_vec_path, extent, dict_lyr_path, key_field, value_field, out_field_name, output_lyr_path):
    # Check for correct inputs
    if not (input_vec_path[-4:]==".shp" and output_lyr_path[-4:]==".shp" and dict_lyr_path[-4:]==".shp"):
        print("wrong input/output layers!")
        return
    
    # Get the dict_feat layer & copy values into the dictionary
    dictDriver = ogr.GetDriverByName("ESRI Shapefile")
    dictDataSource = dictDriver.Open(dict_lyr_path, 0)
    dictLayer = dictDataSource.GetLayer()    
    dict_feat = {}
    print ("-------\nNumber of Entries in shapefile: %i" % dictLayer.GetFeatureCount())
    st = time.time()
    for i in range(0, dictLayer.GetFeatureCount()):
        #if i > 100000: break
        inFeature = dictLayer.GetFeature(i)

        temp1 = inFeature.GetField(key_field)
        temp2 = inFeature.GetField(value_field)
        if temp2 is None:
            temp2 = 0
        
        if dict_feat.has_key(temp1):
            dict_feat[temp1] += temp2
        else:
            if VERBOSE == True: print (temp1)
            dict_feat[temp1] = temp2      
    print ("Loop 1 : %5.2f sec" % (time.time() - st))
    print ("Number of Regions in Dict: %i" % len(dict_feat))
    dictDataSource = None
    # Get the input Layer
    inShapefile = input_vec_path
    inDriver = ogr.GetDriverByName("ESRI Shapefile")
    inDataSource = inDriver.Open(inShapefile, 0)
    inLayer = inDataSource.GetLayer()
    
    
    if CREATE_MEM_LAYER == True :
        #create an input datasource in memory
        inDriverMem=ogr.GetDriverByName('MEMORY')
        inDataSourceMem=inDriverMem.CreateDataSource('memInData')
        #open the memory datasource with write access
        tmp=inDriverMem.Open('memInData',1)
        #copy a layer to memory
        pipes_mem=inDataSourceMem.CopyLayer(inLayer,'pipes',['OVERWRITE=YES'])
        #the new layer can be directly accessed via the handle pipes_mem or as inDataSourceMem.GetLayer('pipes'):
        layer=inDataSourceMem.GetLayer('pipes')

        inLayer = layer
   

   
    if SET_SPATIAL_FILTE == True:
        inLayer.SetSpatialFilterRect(extent[0],extent[2],extent[1],extent[3])
        
        
        
        
    
    
    outShapefile = output_lyr_path
    outDriver = ogr.GetDriverByName("ESRI Shapefile")
    # Remove output shapefile if it already exists
    if os.path.exists(outShapefile):
        outDriver.DeleteDataSource(outShapefile)
    
    # Create the output Layer
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(3035)
    outDriver = ogr.GetDriverByName("ESRI Shapefile")
    
    # Create the output shapefile
    outDataSource = outDriver.CreateDataSource(outShapefile)
    outLayer = outDataSource.CreateLayer("states_centroids", srs, geom_type=ogr.wkbPoint)
    
    if CREATE_MEM_LAYER == True and  0==1:
        
        #create an output datasource in memory
        outDriverMem=ogr.GetDriverByName('MEMORY')
        outDataSourceMem=outDriverMem.CreateDataSource('memOutData')
        #open the memory datasource with write access
        tmp=outDriverMem.Open('memOutData',1)
        #copy a layer to memory
        pipes_mem=outDataSourceMem.CopyLayer(outLayer,'pipes', ['OVERWRITE=YES'])
        #the new layer can be directly accessed via the handle pipes_mem or as outDataSourceMem.GetLayer('pipes'):
        layer=outDataSourceMem.GetLayer('pipes')
        
        outLayer = layer
    
    
    
    
    
    
    
      
    
   
    # Create a field for the output layer
    fieldDefn = ogr.FieldDefn(out_field_name, ogr.OFTReal)
    outLayer.CreateField(fieldDefn)

    # Get the output Layer's Feature Definition
    outLayerDefn = outLayer.GetLayerDefn()
    outfieldName = outLayerDefn.GetFieldDefn(0).GetNameRef()
    
    # Create output Feature
    outFeature = ogr.Feature(outLayerDefn)
            
    # Add features to the ouput Layer
    if VERBOSE == True: print (inLayer.GetFeatureCount())
    print ("-----\nNumber of Entries in Outputlayer: %i" % inLayer.GetFeatureCount())
    j = 0
    dict_feat2 = {}
    st = time.time()
    rows = (extent[1] - extent[0]+1)/1000
    cols = (extent[3] - extent[2]+1)/1000
    #RESULT = np.zeros((rows, cols), dtype="f4")
    for inFeature in inLayer:
        # Get the input Feature
        key_field_name = inFeature.GetField(key_field)
        
        #inFeature.GetField(key_field)
        if dict_feat.has_key(str(key_field_name)):
            if VERBOSE == True: dict_feat2[key_field_name] = ""
            
            geom = inFeature.GetGeometryRef()
            """
            x = geom.Centroid().GetX()
            if x>extent[0] and x<extent[1]:
                y = geom.Centroid().GetY()
                if y>extent[2] and y<extent[3]:
                    RESULT[(y-extent[2])/1000, (x-extent[0])/1000] = dict_feat[key_field_name]
            """    
            j += 1
            # Create output Feature
            #outFeature = ogr.Feature(outLayerDefn)
            # Add field values from input Layer
            outFeature.SetField(outfieldName, dict_feat[key_field_name])
            # Set geometry as centroid
            #geom = inFeature.GetGeometryRef()
            outFeature.SetGeometry(geom.Clone())
            # Add new feature to output Layer
            outLayer.CreateFeature(outFeature)

                            
    inFeature = None
    outFeature = None
    if VERBOSE == True: 
        print ("hits: %i" % j) 
        for key in dict_feat2.keys():
            print (key)
    print ("Loop 2 : %5.2f sec" % (time.time() - st))
    print ("Number of Hits in Output layer: %i" % j)     
    # Save and close DataSources
    inDataSource = None
    outDataSource = None
    
    return 
    
if __name__ == "__main__":
    
    prj_path = "/home/simulant/ag_lukas/personen/Mostafa/HeatDensityMap"
    process_path            = prj_path  + os.sep + "Processed_Data"
    input_vec_path = process_path + os.sep + "Pop_Nuts.shp"
    dict_lyr_path = "/home/simulant/ag_lukas/personen/Mostafa/EnergyDensityII/Data/NUTS_Demand.shp"
    output_lyr_path = process_path + os.sep + "NutsDemand.shp"
    key_field = "NUTS_ID"
    value_field = "ESPON_TOTA"
    out_field_name = "NutsDem"
    
   