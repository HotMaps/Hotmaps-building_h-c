from osgeo import ogr, osr
import os
import numpy as np
CREATE_MEM_LAYER = False
SET_SPATIAL_FILTE = True
VERBOSE = False
#@profile
def query(input_1x1vec_path, extent, NUTS_lyr_path, key_field
          , value_field, out_field_name, output_lyr_path):
    # Check for correct inputs
    if not (input_1x1vec_path[-4:]==".shp" 
            and output_lyr_path[-4:]==".shp" 
            and NUTS_lyr_path[-4:]==".shp"):
        print("wrong input/output layers!")
        return
    
    # Get the dict_feat layer & copy values into the dictionary
    # Walk through NUTS Layer and check whether or not NUTS Region lies within 
    # extent. If so, add NUTS Region to dictionary
    dictDriver = ogr.GetDriverByName("ESRI Shapefile")
    dictDataSource = dictDriver.Open(NUTS_lyr_path, 0)
    dictLayer = dictDataSource.GetLayer()    
    dict_feat = {}
    for i in range(0, dictLayer.GetFeatureCount()):
        inFeature = dictLayer.GetFeature(i)
        geom = inFeature.GetGeometryRef()
        
        x = geom.Centroid().GetX()
        if x>extent[0] and x<extent[1]:
            y = geom.Centroid().GetY()
            if y>extent[2] and y<extent[3]:
                NUTS_ID = inFeature.GetField(key_field)
                NUTS_ROW_ID = inFeature.GetField(value_field)
                
                if NUTS_ID in dict_feat:
                    raise()
                    if not (NUTS_ROW_ID is None):
                        dict_feat[NUTS_ID] += NUTS_ROW_ID
                else:
                    if NUTS_ROW_ID is None:
                        dict_feat[NUTS_ID] = 0
                    else:
                        if VERBOSE == True: print (NUTS_ID)
                        dict_feat[NUTS_ID] = NUTS_ROW_ID      
    dictDataSource = None
    
    # Get the input Layer
    # 1x1 km layer
    inShapefile = input_1x1vec_path
    inDriver = ogr.GetDriverByName("ESRI Shapefile")
    inDataSource = inDriver.Open(inShapefile, 0)
    inLayer = inDataSource.GetLayer()
    
    
    if CREATE_MEM_LAYER == True:
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
    
    if CREATE_MEM_LAYER == True:
        
        #create an output datasource in memory
        outDriverMem=ogr.GetDriverByName('MEMORY')
        outDataSourceMem=outDriverMem.CreateDataSource('memOutData')
        #open the memory datasource with write access
        tmp=outDriverMem.Open('memOutData',1)
        #copy a layer to memory
        pipes_mem=outDataSourceMem.CopyLayer(outLayer,'pipes',srs, ['OVERWRITE=YES'])
        #the new layer can be directly accessed via the handle pipes_mem or as outDataSourceMem.GetLayer('pipes'):
        layer=outDataSourceMem.GetLayer('pipes')
        
        outLayer = layer
        
    
   
    # Create a field for the output layer
    fieldDefn = ogr.FieldDefn(out_field_name, ogr.OFTReal)
    outLayer.CreateField(fieldDefn)

    # Get the output Layer's Feature Definition
    outLayerDefn = outLayer.GetLayerDefn()
      
    # Add features to the ouput Layer
    if VERBOSE == True: print (inLayer.GetFeatureCount())
    j = 0
    # Walk through each feature of the 1x1km shape file which is within the 
    # defined extent
    MapNuts3Array = np.zeros(inLayer.GetFeatureCount(), dtype="uint32")
    out_field_name = outLayerDefn.GetFieldDefn(0).GetNameRef()
    for i, inFeature in enumerate(inLayer):
        # Get the input Feature
        key_field_name = inFeature.GetField(key_field)
        if str(key_field_name) in dict_feat:
            MapNuts3Array[i] = dict_feat[key_field_name]
            
            #if VERBOSE == True: dict_feat2[key_field_name] = ""

            #geom_Centroid = geom.Centroid() 
            #x = geom_Centroid.GetX()
            #if x>extent[0] and x<extent[1]:
            #    y = geom_Centroid.GetY()
            #    if y>extent[2] and y<extent[3]:
            j += 1
            # Create output Feature
            outFeature = ogr.Feature(outLayerDefn)
            # Add field values from input Layer
            outFeature.SetField(out_field_name, dict_feat[key_field_name])
            # Set geometry as centroid
            outFeature.SetGeometry(inFeature.GetGeometryRef().Clone())
            # Add new feature to output Layer
            outLayer.CreateFeature(outFeature)
            
                    
                     
    inFeature = None
    outFeature = None
    if VERBOSE == True: 
        print ("hits: %i out of %i" % (j, inLayer.GetFeatureCount())) 
        """for key in dict_feat2.keys():
            print (key)
        """  
    # Save and close DataSources
    inDataSource = None
    outDataSource = None
    
    return MapNuts3Array
    
if __name__ == "__main__":
    
    prj_path = "/home/simulant/ag_lukas/personen/Mostafa/HeatDensityMap"
    process_path            = prj_path  + os.sep + "Processed_Data"
    input_vec_path = process_path + os.sep + "Pop_Nuts.shp"
    dict_lyr_path = "/home/simulant/ag_lukas/personen/Mostafa/EnergyDensityII/Data/NUTS_Demand.shp"
    output_lyr_path = process_path + os.sep + "NutsDemand.shp"
    key_field = "NUTS_ID"
    value_field = "ESPON_TOTA"
    out_field_name = "NutsDem"
    
   