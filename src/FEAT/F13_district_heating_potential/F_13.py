from src.AD.potential_dh_area.main import default_hdm
from src.CM.CM_TUW4 import district_heating_potential as DHP


def execute(outRasterPath):
    # hdm in raster format from default dataset
    # pix_threshold [GWh/km2]
    # DH_threshold [GWh/a]
    # potential level: NUTS0, 1, 2, 3, own shapefile
    heat_density_map, strd_vector, pix_threshold, DH_threshold = default_hdm()
    # Shapefile of NUTS0, 1, 2, 3 should be available in data warehouse; User
    # should also be able to calculate potential for the selected area: shall
    # be considered in AD
    DHP.NutsCut(heat_density_map, strd_vector, pix_threshold,
                DH_threshold, outRasterPath)


if __name__ == "__main__":
    outRasterPath = "/home/simulant/ag_lukas/personen/Mostafa/" \
                    "test/Pot_AT_TH30_1.tif"
    execute(outRasterPath)
