import os
import time
from osgeo import ogr
from osgeo import osr
import geopandas as gpd
from geopandas.tools import overlay
'''
this code overlays two polygon layers. The possible methods can be seen in dictionary "how_method" within the code.
'''

def overlaying(lyr1_path,lyr2_path,method,outLyr_path):
    how_method = {1: "intersection", 2: "union", 3: "symetrical difference", 4: "difference"}
    lyr1 = gpd.read_file(lyr1_path)
    lyr2 = gpd.read_file(lyr2_path)
    new_lyr = overlay(lyr1, lyr2, how=how_method[method])
    new_lyr.to_file(outLyr_path)


def gdal_intersection(vector_path, filter_lyr_path, outShapefile,
                      outLyrName='outLyr'):
    inDriver = ogr.GetDriverByName("ESRI Shapefile")
    inDataSource = inDriver.Open(vector_path)
    inLayer = inDataSource.GetLayer()
    filterDriver = ogr.GetDriverByName("ESRI Shapefile")
    filterDataSource = filterDriver.Open(filter_lyr_path)
    filterLayer = filterDataSource.GetLayer()
    filterFeat = filterLayer.GetFeature(0)
    filter_geom = filterFeat.GetGeometryRef()
    #(x0, x1, y0, y1) = filterLayer.GetExtent()
    #inLayer.SetSpatialFilterRect(x0, y0, x1, y1)
    inLayer.SetSpatialFilter(filter_geom)
    # set CRS
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(3035)
    outDriver = ogr.GetDriverByName("ESRI Shapefile")
    if os.path.exists(outShapefile):
        outDriver.DeleteDataSource(outShapefile)
    # Create the output shapefile
    outDataSource = outDriver.CreateDataSource(outShapefile)
    geom_typ = inLayer.GetGeomType()
    geom_typ_dict = {1: ogr.wkbPoint, 2: ogr.wkbLineString, 3: ogr.wkbPolygon}
    if geom_typ not in list(geom_typ_dict.keys()):
        raise Exception("Geometry type of the input layer is not supported!")
    outLayer = outDataSource.CreateLayer(outLyrName, srs,
                                         geom_type=geom_typ_dict[geom_typ])
    # Add input Layer Fields to the output Layer
    inLayerDefn = inLayer.GetLayerDefn()
    for i in range(inLayerDefn.GetFieldCount()):
        fieldDefn = inLayerDefn.GetFieldDefn(i)
        outLayer.CreateField(fieldDefn)
    # Get the output Layer's Feature Definition
    outLayerDefn = outLayer.GetLayerDefn()
    counter = 0
    for feat in inLayer:
        counter += 1
        # Get the input Feature
        inFeature = feat
        # Create output Feature
        outFeature = ogr.Feature(outLayerDefn)
        for j in range(inLayerDefn.GetFieldCount()):
            outFeature.SetField(outLayerDefn.GetFieldDefn(j).GetNameRef(),
                                inFeature.GetField(j))
        geom = inFeature.GetGeometryRef()
        outFeature.SetGeometry(geom)
        # Add new feature to output Layer
        outLayer.CreateFeature(outFeature)
        inFeature = None
        outFeature = None
    print(counter)
    # Save and close DataSources
    inDataSource = None
    outDataSource = None


if __name__ == "__main__":
    start = time.time()
    prj_path = "/home/simulant/ag_lukas/personen/Mostafa/Lab"
    lyr1_path = prj_path + os.sep + "Pop_Nuts_Differ.shp"
    lyr2_path = prj_path + os.sep + "Pop_Nuts_merged.shp"
    method=2
    outLyr_path = prj_path + os.sep + "Pop_Nuts_Complete.shp"
    overlaying(lyr1_path, lyr2_path, method, outLyr_path)
    elapsed = time.time() - start
    print('the process took %0.2f seconds' % elapsed)
