from osgeo import ogr,osr
import os,time


def sample_point(input_layer_path, output_lyr_path):
    # Common properties
    inDriver = ogr.GetDriverByName('ESRI Shapefile')
    outDriver = ogr.GetDriverByName("ESRI Shapefile")
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(3035)
    
    inDataSource = inDriver.Open(input_layer_path,0)
    inLayer = inDataSource.GetLayer()
    inLayerDefn = inLayer.GetLayerDefn()
    
    # Create the output Layer
    outShapefile3 = output_lyr_path
    
    # Remove output shapefile if it already exists
    if os.path.exists(outShapefile3):
        outDriver.DeleteDataSource(outShapefile3)
        
    # Create the output shapefile
    outDataSource3 = outDriver.CreateDataSource(outShapefile3)
    outLayer3 = outDataSource3.CreateLayer("population_points",srs, geom_type=ogr.wkbPoint)
    
    for i in range(0, inLayerDefn.GetFieldCount()):
        if i==0:
        #if i==0 or i==3:
            fieldDefn = inLayerDefn.GetFieldDefn(i)
            outLayer3.CreateField(fieldDefn)
    
    # field_name = ogr.FieldDefn("Value", ogr.OFTString)
    # field_name.SetWidth(24)
    # outLayer2.CreateField(field_name)
    # outLayer3.CreateField(field_name)

    outLayerDefn3 = outLayer3.GetLayerDefn()
    
    
    
    # feat = inlayer.GetNextFeature()
    # geom = feat.GetGeometryRef()
    
    for i in range(0, inLayer.GetFeatureCount()):
        # Get the input Feature
        inFeature = inLayer.GetFeature(i)
        geom = inFeature.GetGeometryRef()
        x = geom.Centroid().GetX()
        y = geom.Centroid().GetY()
        for m in range(-5,5):
            for n in range(-5,5):
                point = ogr.Geometry(ogr.wkbPoint)
                outFeature3 = ogr.Feature(outLayerDefn3)
                outFeature3.SetField(outLayerDefn3.GetFieldDefn(0).GetNameRef(), inFeature.GetField(0))                     # 0: population --> Here add for GetField a parameter to understand which field should be taken.
                #outFeature3.SetField(outLayerDefn3.GetFieldDefn(1).GetNameRef(), inFeature.GetField(3))                     # 1,3: demand --> Here add for GetField a parameter to understand which field should be taken.
                point.AddPoint(x + 50*(2*m+1) , y + 50*(2*n+1))
                outFeature3.SetGeometry(point)
                # Add new feature to output Layer
                outLayer3.CreateFeature(outFeature3)
                outFeature3 = None
                point = None
        inFeature = None
    inDataSource = None
    outDataSource3 = None

start_time = time.time()
    
prj_path = "/home/simulant/ag_lukas/personen/Mostafa/EnergyDensityII"            
temp_path            = prj_path  + os.sep + "Temp"
data_path            = prj_path  + os.sep + "Data"    
pop_lyr_path         = temp_path + os.sep + "temp12.shp"
input_lyr_path =     prj_path  + os.sep + "test.shp"
output_lyr_path =     prj_path  + os.sep + "sample.shp"

sample_point(input_lyr_path, output_lyr_path)    

elapsed_time = time.time() - start_time
print(elapsed_time)        