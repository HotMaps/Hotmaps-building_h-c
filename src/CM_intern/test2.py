import gdal
import ogr
import osr
import numpy as np
import os


def array2raster(outRasterPath, rasterOrigin, pixelWidth, pixelHeight,
                 dataType, array, noDataValue):
    '''This function rasterizes the input numpy array '''
    # conversion of data types from numpy to gdal
    dict_varTyp = {"int8":      gdal.GDT_Byte,
                   "int16":     gdal.GDT_Int16,
                   "int32":     gdal.GDT_Int32,
                   "uint16":    gdal.GDT_UInt16,
                   "uint32":    gdal.GDT_UInt32,
                   "float32":   gdal.GDT_Float32,
                   "float64":   gdal.GDT_Float64}
    cols = array.shape[1]
    rows = array.shape[0]
    originX = rasterOrigin[0]
    originY = rasterOrigin[1]
    driver = gdal.GetDriverByName('GTiff')
    outRaster = driver.Create(outRasterPath, cols, rows, 1,
                              dict_varTyp[dataType], ['compress=LZW'])
    outRaster.SetGeoTransform((originX, pixelWidth, 0,
                               originY, 0, pixelHeight))
    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromEPSG(3035)
    outRaster.SetProjection(outRasterSRS.ExportToWkt())
    outRaster.GetRasterBand(1).SetNoDataValue(noDataValue)
    outRaster.GetRasterBand(1).WriteArray(array)
    outRaster.FlushCache()


def hdm(heat_density_map, outRasterPath):
    cutRastDatasource = gdal.Open(heat_density_map)
    transform = cutRastDatasource.GetGeoTransform()
    minx = transform[0]
    maxy = transform[3]
    rasterOrigin = (minx, maxy)
    b11 = cutRastDatasource.GetRasterBand(1)
    arr1 = b11.ReadAsArray().astype(float)
    result = arr1 * 100.0
    array2raster(outRasterPath, rasterOrigin, 100, -100, "float32", result, 0)
    
    
if __name__ == "__main__":
    heat_density_map = "/home/simulant/ag_lukas/personen/Mostafa/" \
                       "DHpot/demand_v2_complete.tif"
    outRasterPath = '/home/simulant/workspace_mostafa/Hotmaps/Hotmaps/src/AD/data_warehouse/top_down_heat_density_map_v2.tif'
    hdm(heat_density_map, outRasterPath)
