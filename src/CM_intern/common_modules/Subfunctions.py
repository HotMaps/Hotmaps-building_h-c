import gdal


'''
Created on Apr 23, 2017

@author: simulant
'''

def rrl(file_name, data_type="f4", raster_band=1):
    #read raster layer and return array
    return read_raster_layer(file_name, data_type, raster_band)
    
    

def read_raster_layer(file_name, data_type="f4", raster_band=1):
    #read raster layer and return array
    print("Reading: %s" % file_name)
    ds = gdal.Open(file_name)
    band = ds.GetRasterBand(raster_band)
    print ("   Got RasterBand")
    arr = band.ReadAsArray().astype(data_type)
    print ("   Done!")
    return  arr
    


        

    