from osgeo import gdal, ogr, osr
import os, time

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

def vec2raster(pixel_size, NoData_value, vector_fn, field, raster_fn):
    xoff, yoff = -pixel_size/2 , pixel_size/2
    # Open the data source and read in the extent
    source_ds = ogr.Open(vector_fn)
    source_layer = source_ds.GetLayer()
    x_min, x_max, y_min, y_max = source_layer.GetExtent()
    # Create the destination data source
    # x_res = int((x_max - x_min) / pixel_size)
    # y_res = int((y_max - y_min) / pixel_size)
    x_res = 55590
    y_res = 44720
    target_ds = gdal.GetDriverByName('GTiff').Create(raster_fn, x_res, y_res, 1, gdal.GDT_Int32, ['compress=LZW'])
    target_ds.SetGeoTransform((x_min+xoff, pixel_size, 0, y_max+yoff, 0, -pixel_size))
    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromEPSG(3035)
    target_ds.SetProjection(outRasterSRS.ExportToWkt())
    band = target_ds.GetRasterBand(1)
    band.SetNoDataValue(NoData_value)

    # Rasterize
    gdal.RasterizeLayer(target_ds, [1], source_layer, burn_values=[0], options=["ATTRIBUTE=%s" %field])

if __name__ == "__main__":
    start_time = time.time()
    pixel_size = 100
    NoData_value = 0
    prj_path = "/home/simulant/ag_lukas/personen/Mostafa/HeatDensityMap"
    org_data_path    = prj_path  + os.sep + "Original Data"
    proc_data_path    = prj_path  + os.sep + "Processed Data"    
    temp_path        = prj_path  + os.sep + "Temp"
    vector_fn = temp_path + os.sep + "NutsPopulation.shp"
    field = "NutsPop"
    raster_fn = temp_path + os.sep + "NutsPopulation.tif"
    vec2raster(pixel_size, NoData_value, vector_fn, field, raster_fn)
    elapsed_time = time.time() - start_time
    print(elapsed_time)