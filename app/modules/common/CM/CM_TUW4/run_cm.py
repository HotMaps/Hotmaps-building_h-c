import os
import time
import sys
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)
from CM.CM_TUW4.polygonize import polygonize
import CM.CM_TUW4.district_heating_potential as DHP
import CM.CM_TUW19.run_cm as CM19


def main(heat_density_map, region, pix_threshold, DH_threshold, output_dir,
         in_orig=None, only_return_areas=False):
    DH_Regions, clipped_hdm, rasterOrigin = DHP.DHReg(heat_density_map, region,
                                                      pix_threshold,
                                                      DH_threshold,
                                                      in_orig)
    if only_return_areas:
        clipped_hdm = rasterOrigin = None
        return DH_Regions
    """
    Outputs:
        DH_Regions: contains binary values (no units) showing coherent areas
        clipped_hdm: hdm after applying pixel threshold [MWh/ha]
        rasterOrigin: Coordination of the top-left corner of raster
    """
    outRasterPath1 = output_dir + os.sep + 'F13_' + 'Pot_areas.tif'
    outRasterPath2 = output_dir + os.sep + 'F13_' + 'labels.tif'
    outShapefilePath = output_dir + os.sep + 'F13_' + 'Pot_AT_TH30.shp'
    DHPot, labels = DHP.DHPotential(DH_Regions, clipped_hdm)
    """save the potentials in shapefile"""
    geo_transform = [rasterOrigin[0], 100, 0, rasterOrigin[1], 0, -100]
    CM19.main(outRasterPath1, geo_transform, 'int16', DH_Regions)
    CM19.main(outRasterPath2, geo_transform, 'int32', labels)
    polygonize(outRasterPath1, outRasterPath2, outShapefilePath, DHPot)
    return outRasterPath1, outShapefilePath


if __name__ == "__main__":
    start = time.time()
    data_warehouse = path + os.sep + 'AD/data_warehouse'
    heat_density_map = data_warehouse + os.sep + 'heat_tot_curr_density_AT.tif'
    region = data_warehouse + os.sep + 'AT.shp'
    output_dir = path + os.sep + 'Outputs'
    outRasterPath = output_dir + os.sep + 'F13_' + 'Pot_AT_TH30.tif'
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    # pix_threshold [MWh/ha]
    pix_threshold = 100
    # DH_threshold [GWh/a]
    DH_threshold = 30
    main(heat_density_map, region, pix_threshold, DH_threshold, outRasterPath)
    elapsed = time.time() - start
    print("%0.3f seconds" % elapsed)
