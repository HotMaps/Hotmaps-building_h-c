import os
import sys
sys.path.insert(0, '../..')
from AD.F13_district_heating_potential.main import ad_f13
from CM.CM_TUW4 import district_heating_potential as DHP
from CM_intern.clip import clip_raster

def execute(outRasterPath):
    # hdm in raster format from default dataset
    # pix_threshold [GWh/km2]
    # DH_threshold [GWh/a]
    # potential level: NUTS0, 1, 2, 3, own shapefile
    heat_density_map, strd_vector, pix_threshold, DH_threshold = ad_f13()
    # Shapefile of NUTS0, 1, 2, 3 should be available in data warehouse; User
    # should also be able to calculate potential for the selected area: shall
    # be considered in AD
    DH_Regions, arr1, origin = DHP.DHReg(heat_density_map, strd_vector,
                                         pix_threshold, DH_threshold)
    result = DHP.DHPotential(DH_Regions, arr1)
    DHP.array2raster(outRasterPath, origin, 100, -100, "float32", result, 0)
    result = arr1 * DH_Regions.astype(int)
    # create raster cuts and summations
    geoTrans = [origin[0], 100, 0, origin[1], 0, -100]
    output_dir = os.getcwd() + os.sep + 'Outputs'
#     clip_raster(rast, features_path, outRasterDir, gt=None, nodata=-9999,
#                 save2csv=None, save2raster=None, save2shp=None,
#                 unit_multiplier=None)
    clip_raster(result, strd_vector, output_dir, gt=geoTrans, nodata=0,
                save2csv=True, save2raster=True, save2shp=True,
                unit_multiplier=0.01)


if __name__ == "__main__":
    os.chdir('../..')
    output_dir = os.getcwd() + os.sep + 'Outputs'
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    outRasterPath = output_dir + os.sep + 'Pot_AT_TH30.tif'
    os.chdir(os.getcwd() + '/FEAT/F13_intern')
    execute(outRasterPath)
