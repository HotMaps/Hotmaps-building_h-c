'''
Created on Apr 20, 2017

@author: simulant
'''
import os


def ad_f63(spec_demand_csv, building_strd_info_csv, inShapefile):
    [process0, process1, process2] = [True] * 3
    # path to the src
    path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                           abspath(__file__))))
    output_dir = path + os.sep + 'Outputs'
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    data_warehouse = path + os.sep + 'AD/data_warehouse_intern'
    eu_shp = data_warehouse + os.sep + 'AT_NUTS3.shp'
    if spec_demand_csv == '':
        # average specific demand in EU countries in residential and service
        # sector
        spec_demand_csv = data_warehouse + os.sep + 'useful_demand.csv'
        UsefulDemandRasterPath = data_warehouse
        UsefulDemandRaster = [UsefulDemandRasterPath +
                              '/ResidentialUsefulDemand.tif',
                              UsefulDemandRasterPath +
                              '/ServiceUsefulDemand.tif']
        process0 = False
    else:
        UsefulDemandRasterPath = output_dir
        UsefulDemandRaster = [output_dir + '/F63_ResidentialUsefulDemand.tif',
                              output_dir + '/F63_ServiceUsefulDemand.tif']
    outShapefile = output_dir + os.sep + 'F63_updated_building_footprint.shp'
    if building_strd_info_csv == '':
        building_strd_info_csv = output_dir + os.sep + 'F63_building' \
                                                       '_strd_info.csv'
    else:
        process1 = False
    if inShapefile == '':
        # here, OSM cut for the selected region should be attributed to
        # the inShapefile
        inShapefile = data_warehouse + os.sep + 'Sample_OSM_Building_Lyr.shp'
        process2 = False
    if inShapefile == '' and building_strd_info_csv != '':
        process1 = False
    # to be added from data warehouse as soon as available
    population = 1000000
    heatDensityRaster = output_dir + os.sep + 'F63_Heat_Density_Map.tif'
    process_bool = (process0, process1, process2)
    inputValues = (eu_shp, spec_demand_csv, UsefulDemandRasterPath,
                   UsefulDemandRaster, inShapefile, building_strd_info_csv,
                   outShapefile, heatDensityRaster, population)
    return process_bool, inputValues


if __name__ == "__main__":
    spec_demand_csv = ''
    inShapefile = ''
    building_strd_info_csv = ''
    output = ad_f63(spec_demand_csv, building_strd_info_csv, inShapefile)
    for item0 in output:
        for item in item0:
            print(item)
