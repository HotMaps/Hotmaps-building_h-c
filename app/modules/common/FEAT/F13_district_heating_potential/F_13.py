import os
import sys
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)
from AD.F13_district_heating_potential.main import ad_f13
import CM.CM_TUW4.run_cm as CM4



def execute(output_dir):
    '''
    hdm in raster format from default dataset
    pix_threshold [MWh/ha]
    DH_threshold [GWh/a]
    potential level: NUTS0, 1, 2, 3, own shapefile
    '''
    heat_density_map, strd_vector, pix_threshold, DH_threshold = ad_f13()
    '''
    Shapefile of NUTS0, 1, 2, 3 should be available in data warehouse; User
    should also be able to calculate potential for the selected area: shall
    be considered in AD
    Outputs:
        DH_Regions: contains binary values (no units) showing coherent areas
        shapefile: showing coherent areas and their DH potential
    '''
    outRasterPath, outShapefile = CM4.main(heat_density_map, strd_vector,
                                           pix_threshold, DH_threshold,
                                           output_dir)
    return {'F13_out_raster_path_0': outRasterPath,
            'F13_out_shapefile_path_0': outShapefile}


if __name__ == "__main__":
    output_dir = path + os.sep + 'Outputs'
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    output = execute(output_dir)
    print(output)
