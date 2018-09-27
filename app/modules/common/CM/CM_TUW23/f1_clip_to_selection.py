import os
import sys
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)
from CM.CM_TUW0.rem_mk_dir import rm_file
from CM.CM_TUW1.read_raster import read_raster_by_feature as RAbF
from CM.CM_TUW22 import run_cm as CM22


def raster_cut(raster_path, features_path, output_dir, cut_name):
    shpName = features_path.replace('\\', '/')
    shpName = shpName.split('/')[-1][0:-4]
    raster_cut_old = output_dir + os.sep + shpName + '_feature_0.tif'
    raster_cut_new = output_dir + os.sep + cut_name + '.tif'
    rm_file(raster_cut_old, raster_cut_new)
    array, gt = RAbF(features_path, raster_path, return_gt=True)
    CM22.main(array, features_path, output_dir, gt, nodata=0, save2raster=True)
    os.rename(raster_cut_old, raster_cut_new)
    os.rename(raster_cut_old[:-3]+'tfw', raster_cut_new[:-3]+'tfw')
    return raster_cut_new
