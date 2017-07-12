import os
from src.AD.F13_district_heating_potential.main import ad_f13
from src.CM.CM_TUW4 import district_heating_potential as DHP


def execute(outRasterPath):
    # hdm in raster format from default dataset
    # pix_threshold [GWh/km2]
    # DH_threshold [GWh/a]
    # potential level: NUTS0, 1, 2, 3, own shapefile
    heat_density_map, strd_vector, pix_threshold, DH_threshold = ad_f13()
    # Shapefile of NUTS0, 1, 2, 3 should be available in data warehouse; User
    # should also be able to calculate potential for the selected area: shall
    # be considered in AD
    DHP.NutsCut(heat_density_map, strd_vector, pix_threshold,
                DH_threshold, outRasterPath)


if __name__ == "__main__":
    os.chdir('../..')
    output_dir = os.getcwd() + os.sep + 'Outputs'
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    outRasterPath = output_dir + os.sep + 'Pot_AT_TH30.tif'
    os.chdir(os.getcwd() + '/FEAT/F13_district_heating_potential')
    execute(outRasterPath)
