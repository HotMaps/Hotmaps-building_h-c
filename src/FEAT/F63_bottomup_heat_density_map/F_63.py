import os
import sys
sys.path.insert(0, '../..')
from AD.F63_bu_heat_density_map.main import ad_f63
from CM.CM_TUW9 import main_block


def execute(spec_demand_csv, building_strd_info_csv, inShapefile):
    if spec_demand_csv != '' and spec_demand_csv[-4:] != '.csv':
        raise ValueError('A comma separated file should be selected!')
    if inShapefile != '' and inShapefile[-4:] != '.shp':
        raise ValueError('A shapefile should be selected!')
    process_bool, inputValues = ad_f63(spec_demand_csv,
                                       building_strd_info_csv, inShapefile)
    main_block.main(process_bool, inputValues)


if __name__ == "__main__":
    os.chdir('../..')
    output_dir = os.getcwd() + os.sep + 'Outputs'
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    os.chdir(os.getcwd() + '/FEAT/F63_bottomup_heat_density_map')
    ###########################################################################
    spec_demand_csv = ''
    building_strd_info_csv = ''
    inShapefile = ''
    execute(spec_demand_csv, building_strd_info_csv, inShapefile)
