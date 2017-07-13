'''
Created on Apr 20, 2017

@author: simulant
'''
import os


def ad_f63(spec_demand_csv, building_strd_info_csv, inShapefile):
    [process0, process1, process2] = [True] * 3
    os.chdir('../..')
    output_dir = os.getcwd() + os.sep + 'Outputs'
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    data_warehouse = os.getcwd() + os.sep + 'AD/data_warehouse'
    eu_shp = data_warehouse + os.sep + 'EU28_plus_CH.shp'
    if spec_demand_csv == '':
        # average specific demand in EU countries in residential and service sector
        spec_demand_csv = data_warehouse + os.sep + 'useful_demand.csv'
        UsefulDemandRasterPath = data_warehouse
        UsefulDemandRaster = [UsefulDemandRasterPath +
                              '/ResidentialUsefulDemand.tif',
                              UsefulDemandRasterPath +
                              '/ServiceUsefulDemand.tif']
        process0 = False
    else:
        UsefulDemandRasterPath = output_dir
        UsefulDemandRaster = [output_dir + '/ResidentialUsefulDemand.tif',
                              output_dir + '/ServiceUsefulDemand.tif']
    outShapefile = output_dir + os.sep + 'updated_building_footprint.shp'
    if building_strd_info_csv == '':
        building_strd_info_csv = output_dir + os.sep + 'building_strd_info.csv'
    else:
        process1 = False
    if inShapefile == '':
        # here, OSM cut for the selected region should be attributed to
        # the inShapefile
        inShapefile = data_warehouse + os.sep + 'gis.osm_buildings_a_free_1' \
                                                '_3035.shp'
        process2 = False
    if inShapefile == '' and building_strd_info_csv != '':
        process1 = False
    # to be added from data warehouse as soon as available
    population = 1000000
    heatDensityRaster = output_dir + os.sep + 'Heat_Density_Map.tif'
    process_bool = (process0, process1, process2)
    inputValues = (eu_shp, spec_demand_csv, UsefulDemandRasterPath,
                   UsefulDemandRaster, inShapefile, building_strd_info_csv,
                   outShapefile, heatDensityRaster, population)
    return process_bool, inputValues


if __name__ == "__main__":
    spec_demand_csv = ''
    inShapefile = ''
    building_strd_info_csv = ''
    ad_f63(spec_demand_csv, building_strd_info_csv, inShapefile)