from osgeo import gdal
from osgeo import ogr
from osgeo import osr
import sys

def polygonize():
    # this allows GDAL to throw Python Exceptions
    gdal.UseExceptions()

    #
    #  get raster datasource
    #
    inRasterPath = "/home/simulant/ag_lukas/personen/Mostafa/potDH/Pot_EU28_TH30_final.tif"
    src_ds = gdal.Open( inRasterPath )
    if src_ds is None:
        print 'Unable to open %s' % src_filename
        sys.exit(1)

    try:
        srcband = src_ds.GetRasterBand(1)
    except RuntimeError, e:
        # for example, try GetRasterBand(10)
        print 'Band ( %i ) not found' % band_num
        print e
        sys.exit(1)

    srs = osr.SpatialReference()
    srs.ImportFromEPSG(3035)
        
        
    #
    #  create output datasource
    #
    dst_layername = "POLYGONIZED_STUFF"
    drv = ogr.GetDriverByName("ESRI Shapefile")
    dst_ds = drv.CreateDataSource( inRasterPath[:-3]+"shp" )
    dst_layer = dst_ds.CreateLayer(dst_layername, srs )

    gdal.Polygonize( srcband, None, dst_layer, -1, [], callback=None )
    
if __name__ == "__main__":
    polygonize()