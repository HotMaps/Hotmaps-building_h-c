import gdal, osr



'''
To create the raster consider following data types:

GDT_Unknown     Unknown or unspecified type
GDT_Byte        Eight bit unsigned integer
GDT_UInt16      Sixteen bit unsigned integer
GDT_Int16       Sixteen bit signed integer
GDT_UInt32      Thirty two bit unsigned integer
GDT_Int32       Thirty two bit signed integer
GDT_Float32     Thirty two bit floating point
GDT_Float64     Sixty four bit floating point
GDT_CInt16      Complex Int16
GDT_CInt32      Complex Int32
GDT_CFloat32    Complex Float32
GDT_CFloat64    Complex Float64
'''

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