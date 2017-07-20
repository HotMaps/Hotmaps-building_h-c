from osgeo import ogr, osr
import os

def polycent(inLayerPath, outLayerPath):
    # Check for correct inputs
    if not (inLayerPath[-4:]==".shp" and outLayerPath[-4:]==".shp"):
        print("wrong input/output layers!")
        return
    
    # Get the input Layer
    inShapefile = inLayerPath
    inDriver = ogr.GetDriverByName("ESRI Shapefile")
    inDataSource = inDriver.Open(inShapefile, 0)
    inLayer = inDataSource.GetLayer()
    
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(3035)
    
    # Create the output Layer
    outShapefile = outLayerPath
    outDriver = ogr.GetDriverByName("ESRI Shapefile")

    # Remove output shapefile if it already exists
    if os.path.exists(outShapefile):
        outDriver.DeleteDataSource(outShapefile)

    # Create the output shapefile
    outDataSource = outDriver.CreateDataSource(outShapefile)
    outLayer = outDataSource.CreateLayer("states_centroids", srs, geom_type=ogr.wkbPoint)
    
    # Add input Layer Fields to the output Layer
    inLayerDefn = inLayer.GetLayerDefn()
        
    for i in range(0, inLayerDefn.GetFieldCount()):
        fieldDefn = inLayerDefn.GetFieldDefn(i)
        outLayer.CreateField(fieldDefn)

    # Get the output Layer's Feature Definition
    outLayerDefn = outLayer.GetLayerDefn()
    


    # Add features to the ouput Layer
    for i in range(0, inLayer.GetFeatureCount()):
        # Get the input Feature
        inFeature = inLayer.GetFeature(i)
        # Create output Feature
        outFeature = ogr.Feature(outLayerDefn)
        # Add field values from input Layer
        for j in range(0, outLayerDefn.GetFieldCount()):
            outFeature.SetField(outLayerDefn.GetFieldDefn(j).GetNameRef(), inFeature.GetField(j))
        # Set geometry as centroid
        geom = inFeature.GetGeometryRef()
        centroid = geom.Centroid()        
        outFeature.SetGeometry(centroid)
        # Add new feature to output Layer
        outLayer.CreateFeature(outFeature)
        inFeature = None
        outFeature = None
        
    # Save and close DataSources
    inDataSource = None
    outDataSource = None
    
if __name__ == "__main__":
    
    prj_path = "/home/simulant/ag_lukas/personen/Mostafa/EnergyDensityII"
    temp_path            = prj_path  + os.sep + "Temp"
    data_path            = prj_path  + os.sep + "Data"
    inLayerPath = prj_path + os.sep + "Geostat_pop.shp"
    outLayerPath = prj_path + os.sep + "pop_centroid.shp"
    
    polycent(inLayerPath, outLayerPath)