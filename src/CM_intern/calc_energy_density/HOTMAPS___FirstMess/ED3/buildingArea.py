from osgeo import ogr, osr
import os
import time

def area(input_vec_path, dict_lyr_path):
    start = time.time()
    dictDriver = ogr.GetDriverByName("ESRI Shapefile")
    dictDataSource = dictDriver.Open(dict_lyr_path, 0)
    dictLayer = dictDataSource.GetLayer()
    areaL = []
    
    inDriver = ogr.GetDriverByName("ESRI Shapefile")
    inDataSource = inDriver.Open(input_vec_path, 0)
    inLayer = inDataSource.GetLayer()
    extent = inLayer.GetExtent()
    
    for i in range(0, dictLayer.GetFeatureCount()):
        inFeature = dictLayer.GetFeature(i)
        geom = inFeature.GetGeometryRef()
        fminx, fmaxx, fminy, fmaxy = geom.GetEnvelope()
        if fminx >= extent[0]:
            if fmaxx <= extent[1]:
                if fminy >= extent[2]:
                    if fmaxy <= extent[3]:
                        inLayer.SetSpatialFilterRect(fminx,fminy,fmaxx,fmaxy)
                    else:
                        continue
                else:
                    continue
            else:
                continue
        else:
            continue
        area_ = 0
        for inFeature in inLayer:
            geom = inFeature.GetGeometryRef()
            area_ += geom.GetArea()
        areaL.append(area_)
            #inLayer.SetSpatialFilter(NULL)
        
        
    print(areaL)
    elapsedtime = time.time() - start
    print(elapsedtime)
    
    
if __name__ == "__main__":
    input_vec_path = "/home/simulant/workspace/project/HOTMAPS/openstreetmap/extract/austria/gis.osm_buildings_a_free_1_3035.shp"
    dict_lyr_path = "/home/simulant/ag_lukas/personen/Mostafa/HeatDensityMap - Copy/Original Data/NUTS3.shp"
    area(input_vec_path, dict_lyr_path)