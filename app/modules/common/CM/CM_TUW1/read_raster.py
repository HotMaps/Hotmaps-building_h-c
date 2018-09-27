import os
from osgeo import gdal
from osgeo import ogr
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
from CM.CM_TUW20 import run_cm as CM20


def raster_array(raster, dType=float, return_gt=None):
    ds = gdal.Open(raster)
    geo_transform = ds.GetGeoTransform()
    band1 = ds.GetRasterBand(1)
    arr = band1.ReadAsArray().astype(dType)
    ds = None
    if return_gt:
        return arr, geo_transform
    else:
        return arr


def read_raster_by_feature(feature, raster, dType=float, return_gt=None):
    # get the extent of the shapefile
    inDriver = ogr.GetDriverByName("ESRI Shapefile")
    inDataSource = inDriver.Open(feature, 0)
    inLayer = inDataSource.GetLayer()
    shp_minX, shp_maxX, shp_minY, shp_maxY = inLayer.GetExtent()
    # get the extent of the raster file
    ds = gdal.Open(raster)
    geo_transform = ds.GetGeoTransform()
    gt = list(geo_transform)
    col = ds.RasterXSize
    row = ds.RasterYSize
    minx = geo_transform[0]
    maxy = geo_transform[3]
    # calculate xoffset, yoffset, xdim and ydim for reading from raster
    (lowIndexX, upIndexX, lowIndexY, upIndexY) = CM20.main(minx, maxy,
                                                           row, col,
                                                           shp_minX, shp_maxX,
                                                           shp_minY, shp_maxY,
                                                           geo_transform[1],
                                                           -geo_transform[5])
    xdim = upIndexY - lowIndexY
    ydim = upIndexX - lowIndexX
    band1 = ds.GetRasterBand(1)
    arr = band1.ReadAsArray(lowIndexY, lowIndexX, xdim, ydim).astype(dType)
    ds = inDataSource = None
    if return_gt:
        gt[0] = minx + 100 * lowIndexY
        gt[3] = maxy - 100 * lowIndexX
        return arr, gt
    else:
        return arr
