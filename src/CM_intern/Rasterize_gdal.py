import ogr, gdal, osr

def gdal_rasterize(vector_fn, raster_fn, targetfield, pixel_size, NoData_value, extention):
    
    

    # Filename of the raster Tiff that will be created
    #raster_fn = outRasterPath
    
    # Open the data source and read in the extent
    source_ds = ogr.Open(vector_fn)
    source_layer = source_ds.GetLayer()
    
    
    # The following 
    (x_min, x_max, y_min, y_max) = extention
    
    # Create the destination data source
    x_res = int((x_max - x_min) / pixel_size)
    y_res = int((y_max - y_min) / pixel_size)
    
    target_ds = gdal.GetDriverByName('GTiff').Create(raster_fn, x_res, y_res, 1, gdal.GDT_Float32, ['compress=LZW'])
    target_ds.SetGeoTransform((x_min, pixel_size, 0, y_max, 0, -pixel_size))
    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromEPSG(3035)
    target_ds.SetProjection(outRasterSRS.ExportToWkt())
    band = target_ds.GetRasterBand(1)
    band.SetNoDataValue(NoData_value)
    
    # Rasterize
    gdal.RasterizeLayer(target_ds,[1], source_layer, options=["ATTRIBUTE=%s" %targetfield])
    target_ds = None
    source_layer = None
    source_ds = None
    
if __name__ == "__main__":
    # Define pixel_size and NoData value of new raster
    pixel_size = 100
    NoData_value = 0
    extention = (944000, 6503000, 942000, 5414000)
    targetfield = 'Resid.'
    vector_fn = "/home/simulant/ag_lukas/personen/Mostafa/Task 3.1/NoDemandData/EnergyUseEU28.shp"
    raster_fn = "/home/simulant/ag_lukas/personen/Mostafa/Task 3.1/NoDemandData/ResidentialUsefulDemand.tif"
    gdal_rasterize(vector_fn, raster_fn, targetfield, pixel_size, NoData_value, extention)