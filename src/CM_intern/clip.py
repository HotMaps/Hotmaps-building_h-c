import os
import sys
import time
from osgeo import gdal
from osgeo import gdalnumeric
from osgeo import ogr
from PIL import Image, ImageDraw
import numpy as np
import pandas as pd
path = os.path.dirname(os.path.dirname(__file__))
if path not in sys.path:
    sys.path.append(path)
from CM_intern import csv2shp
import CM.CM_TUW19.run_cm as CM19


def saveCSVorSHP(feat, demand, outCSVDir, save2csv=None, save2shp=None,
                 inCSV=None, outShpPath=None):
    df = pd.DataFrame()
    df['Feature'] = np.array(feat)
    df['Sum'] = np.array(demand)
    csv_path = outCSVDir + os.sep + 'clip_result.csv'
    if save2csv:
        df.to_csv(csv_path)
    if save2shp:
        csv2shp.Excel2shapefile(features_path, df, outShpPath)


def clip_raster(rast, features_path, outRasterDir, gt=None, nodata=-9999,
                save2csv=None, save2raster=None, save2shp=None,
                unit_multiplier=None, return_array=False):
    '''
    Clips a raster (given as either a gdal.Dataset or as a numpy.array
    instance) to a polygon layer provided by a Shapefile (or other vector
    layer). If a numpy.array is given, a "GeoTransform" must be provided
    (via dataset.GetGeoTransform() in GDAL). Returns an array. Clip features
    can be multi-part geometry and with interior ring inside them.
    Modified version of the code provided in:
    karthur.org/2015/clipping-rasters-in-python.html

    #clip-a-geotiff-with-shapefile

    Arguments:
        rast               A gdal.Dataset or a NumPy array
        features_path      The path to the clipping layer
        gt                 An optional GDAL GeoTransform to use instead
        nodata             The NoData value; defaults to -9999
        save2csv           should the outputs be saved in a csv file as well?
        unit_multiplier    Factor to be multiplied into the summation to
                           output the desired unit.
    '''

    def image_to_array(i):
        '''
        Converts a Python Imaging Library (PIL) array to a gdalnumeric image.
        '''
        a = gdalnumeric.fromstring(i.tobytes(), 'b')
        a.shape = i.im.size[1], i.im.size[0]
        return a

    def world_to_pixel(geo_matrix, x, y):
        '''
        Uses a gdal geomatrix (gdal.GetGeoTransform()) to calculate
        the pixel location of a geospatial coordinate; from:
        http://pcjericks.github.io/py-gdalogr-cookbook/raster_layers.html

        clip-a-geotiff-with-shapefile
        '''
        ulX = geo_matrix[0]
        ulY = geo_matrix[3]
        xDist = geo_matrix[1]
        yDist = geo_matrix[5]
        rtnX = geo_matrix[2]
        rtnY = geo_matrix[4]
        pixel = int((x - ulX) / xDist)
        line = int((ulY - y) / xDist)
        return (pixel, line)

    # get shapefile name
    shpName = features_path.replace('\\', '/')
    shpName = shpName.split('/')[-1][0:-4]
    # Create a data array for the output csv
    if save2csv:
        feat = []
        demand = []
    if unit_multiplier is None:
        unit_multiplier = 1.0
    # Can accept either a gdal.Dataset or numpy.array instance
    if not isinstance(rast, np.ndarray):
        gt = rast.GetGeoTransform()
        rast = rast.ReadAsArray()

    # Create an OGR layer from a boundary shapefile
    features = ogr.Open(features_path)
    if features.GetDriver().GetName() == 'ESRI Shapefile':
        temp = os.path.split(os.path.splitext(features_path)[0])
        lyr = features.GetLayer(temp[1])
    else:
        lyr = features.GetLayer()
    for fid in range(lyr.GetFeatureCount()):
        '''
        if fid > 40:
            continue
        '''
        poly = lyr.GetFeature(fid)
        geom = poly.GetGeometryRef()
        # Convert the feature extent to image pixel coordinates
        minX, maxX, minY, maxY = geom.GetEnvelope()
        ulX, ulY = world_to_pixel(gt, minX, maxY)
        lrX, lrY = world_to_pixel(gt, maxX, minY)
        # Calculate the pixel size of the new image
        pxWidth = int(lrX - ulX)
        pxHeight = int(lrY - ulY)
        # If the clipping features extend out-of-bounds and ABOVE the raster...
        if gt[3] < maxY:
            # In such a case... ulY ends up being negative--can't have that!
            iY = ulY
            ulY = 0
        try:
            clip = rast[:, ulY:lrY, ulX:lrX]
            clip_complete = np.zeros_like(clip, clip.dtype)
        except IndexError:
            clip = rast[ulY:lrY, ulX:lrX]
            clip_complete = np.zeros_like(clip, clip.dtype)
        geometry_counts = geom.GetGeometryCount()
        # perform the process for multi-part features
        for i in range(geometry_counts):
            # Multi-band image?
            try:
                clip = rast[:, ulY:lrY, ulX:lrX]
            except IndexError:
                clip = rast[ulY:lrY, ulX:lrX]
            # Create a new geomatrix for the image
            gt2 = list(gt)
            gt2[0] = gt2[1]*int(minX/gt2[1])
            gt2[3] = gt2[1]*int(maxY/gt2[1])
            if gt2[3] < maxY:
                gt2[3] = gt2[1] * int(maxY/gt2[1] + 1)
            # Map points to pixels for drawing the boundary on a blank 8-bit,
            # black and white, mask image.
            points = []
            pixels = []
            # check multi-part geometries
            if geometry_counts > 1:
                geom1 = geom.GetGeometryRef(i)
                # check multi-part geometry with interior ring
                if geom1.GetGeometryName() == 'LINEARRING':
                    pts = geom1
                else:
                    # get outer ring of polygon
                    pts = geom1.GetGeometryRef(0)
                # print(geom1.GetGeometryName() + ' ' + pts.GetGeometryName())
            else:
                # get outer ring of polygon
                pts = geom.GetGeometryRef(0)
            for p in range(pts.GetPointCount()):
                points.append((pts.GetX(p), pts.GetY(p)))
            for p in points:
                pixels.append(world_to_pixel(gt2, p[0], p[1]))
            raster_poly = Image.new('L', (pxWidth, pxHeight), 1)
            rasterize = ImageDraw.Draw(raster_poly)
            # Fill with zeroes
            rasterize.polygon(pixels, 0)
            # If the clipping features extend out-of-bounds and ABOVE the
            # raster
            if gt[3] < maxY:
                # The clip features were "pushed down" to match the bounds of
                # the raster; this step "pulls" them back up
                premask = image_to_array(raster_poly)
                # We slice out the piece of our clip features that are
                # "off the map"
                mask = np.ndarray((premask.shape[-2] - abs(iY),
                                   premask.shape[-1]), premask.dtype)
                mask[:] = premask[abs(iY):, :]
                # Then fill in from the bottom
                mask.resize(premask.shape, refcheck=False)
                # Most importantly, push the clipped piece down
                gt2[3] = maxY - (maxY - gt[3])
            else:
                mask = image_to_array(raster_poly)
            # Clip the image using the mask
            try:
                clip = gdalnumeric.choose(mask, (clip, nodata))
            # If the clipping features extend out-of-bounds and BELOW
            # the raster
            except ValueError:
                # We have to cut the clipping features to the raster!
                rshp = list(mask.shape)
                if mask.shape[-2] != clip.shape[-2]:
                    rshp[0] = clip.shape[-2]
                if mask.shape[-1] != clip.shape[-1]:
                    rshp[1] = clip.shape[-1]
                mask.resize(*rshp, refcheck=False)
                clip = gdalnumeric.choose(mask, (clip, nodata))
            m1, n1 = np.nonzero(clip)
            clip_stack = set(list(zip(m1, n1)))
            m2, n2 = np.nonzero(clip_complete)
            clip_complete_stack = set(list(zip(m2, n2)))
            intersect_clip = clip_complete_stack.intersection(clip_stack)
            if len(intersect_clip) == 0:
                clip_complete = clip_complete + clip
            else:
                clip_complete = clip_complete - clip
            mask = None
            premask = None
            raster_poly = None
            rasterize = None
            geom1 = None
            pts = None
            gt3 = gt2
            gt2 = None
            clip = None
        if save2csv:
            nuts_region = str(poly.GetField(0))
            dem_sum = np.sum(clip_complete) * unit_multiplier
            feat.append(nuts_region)
            demand.append(dem_sum)
            print('Total demand/potential in nuts region %s is: %0.1f GWh'
                  % (nuts_region, dem_sum))
        if save2raster:
            outRasterPath = outRasterDir + os.sep + shpName + '_feature_' + \
                            str(fid) + '.tif'
            CM19.main(outRasterPath, gt3, str(clip_complete.dtype),
                      clip_complete, 0)
        if save2csv or save2shp:
            outCSVDir = outRasterDir
            saveCSVorSHP(feat, demand, outCSVDir, save2csv=None, save2shp=None,
                         inCSV=None, outShpPath=None)
        if return_array:
            return clip_complete, gt3

if __name__ == '__main__':
    start = time.time()
    # path to the src
    data_warehouse = path + os.sep + 'AD/data_warehouse'
    features_path = data_warehouse + os.sep + "AT.shp"
    raster = data_warehouse + os.sep + "top_down_heat_density_map_v2_AT.tif"
    output_dir = path + os.sep + 'Outputs'
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    nodata = 0
    rast = gdal.Open(raster)
    outRasterDir = output_dir
    clip_raster(rast, features_path, outRasterDir, save2raster=True, nodata=0)
    print(time.time() - start)
