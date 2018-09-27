import os
import sys
from osgeo import ogr
from osgeo import osr
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)


def change_projection(inShapefile, outShapefile, outEPSG=3035):
    inDriver = ogr.GetDriverByName('ESRI Shapefile')
    inDataSource = inDriver.Open(inShapefile)
    inLayer = inDataSource.GetLayer()
    inSpatialRef = inLayer.GetSpatialRef()
    # Desired projection is EPSG3035
    outSpatialRef = osr.SpatialReference()
    outSpatialRef.ImportFromEPSG(outEPSG)
    coordTrans = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)
    geom_typ = inLayer.GetGeomType()
    geom_typ_dict = {1: ogr.wkbPoint,
                     2: ogr.wkbLineString,
                     3: ogr.wkbPolygon}
    outDriver = ogr.GetDriverByName("ESRI Shapefile")
    if os.path.exists(outShapefile):
        outDriver.DeleteDataSource(outShapefile)
    # Create the output shapefile
    outDataSource = outDriver.CreateDataSource(outShapefile)
    outLayer = outDataSource.CreateLayer('outLyr', outSpatialRef,
                                         geom_type=geom_typ_dict[geom_typ])
    inLayerDefn = inLayer.GetLayerDefn()
    f_counts = inLayerDefn.GetFieldCount()
    for i in range(f_counts):
        fieldDefn = inLayerDefn.GetFieldDefn(i)
        outLayer.CreateField(fieldDefn)
    outLayerDefn = outLayer.GetLayerDefn()
    for feature in inLayer:
        outFeature = ogr.Feature(outLayerDefn)
        # Add field values from input Layer
        for i in range(outLayerDefn.GetFieldCount()):
            outFeature.SetField(outLayerDefn.GetFieldDefn(i).GetNameRef(),
                                feature.GetField(i))
        geom = feature.GetGeometryRef()
        geom.Transform(coordTrans)
        outFeature.SetGeometry(geom)
        # Add new feature to output Layer
        outLayer.CreateFeature(outFeature)
        outFeature = None
    inDataSource = None
    outDataSource = None
