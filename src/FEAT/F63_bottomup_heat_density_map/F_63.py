import os
import sys
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)
from AD.F63_bu_heat_density_map.main import ad_f63
import CM.CM_TUW9.run_cm as CM9


def execute(spec_demand_csv, building_strd_info_csv, inShapefile):
    if spec_demand_csv != '' and spec_demand_csv[-4:] != '.csv':
        raise ValueError('A comma separated file should be selected!')
    if inShapefile != '' and inShapefile[-4:] != '.shp':
        raise ValueError('A shapefile should be selected!')
    process_bool, inputValues = ad_f63(spec_demand_csv,
                                       building_strd_info_csv, inShapefile)
    CM9.main(process_bool, inputValues)


if __name__ == "__main__":
    print('Calculation started!')
    output_dir = path + os.sep + 'Outputs'
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    ###########################################################################
    spec_demand_csv = ''
    building_strd_info_csv = ''
    inShapefile = ''
    execute(spec_demand_csv, building_strd_info_csv, inShapefile)
    print('Calculation ended successfully!')
