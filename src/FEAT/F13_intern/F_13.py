import os
import sys
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)
from AD.F13_district_heating_potential.main import ad_f13
import CM.CM_TUW4.run_cm as CM4
import CM.CM_TUW19.run_cm as CM19
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
    DH_Regions, arr1, origin = CM4.main(heat_density_map, strd_vector,
                                         pix_threshold, DH_threshold)
    pot_result = CM4.DHPotential(DH_Regions, arr1)
    geo_transform = [origin[0], 100, 0, origin[1], 0, -100]
    CM19.main(outRasterPath, geo_transform, str(pot_result.dtype), pot_result)
    pix_result = arr1 * DH_Regions.astype(int)
    # create raster cuts and summations
    output_dir = path + os.sep + 'Outputs'
    clip_raster(pix_result, strd_vector, output_dir, gt=geo_transform,
                nodata=0, save2csv=True, save2raster=True, save2shp=True,
                unit_multiplier=0.01)


if __name__ == "__main__":
    print('Calculation started!')
    output_dir = path + os.sep + "Outputs"
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    outRasterPath = output_dir + os.sep + 'F13intern_Pot_AT_TH30.tif'
    execute(outRasterPath)
    print('Calculation ended successfully!')
