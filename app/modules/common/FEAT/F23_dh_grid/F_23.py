import os
import sys
import time
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                     abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)
from AD.F23_dh_grid.main import ad_f23
import CM.CM_TUW23.run_cm as CM23


def execute(case_study, output_dir):
    pixT, DHT, gfa_path, hdm_path = ad_f23()
    output_summary = CM23.main(case_study, pixT, DHT, gfa_path, hdm_path,
                               output_dir)
    return output_summary
    

if __name__ == '__main__':
    start = time.time()
    output_dir = path + os.sep + 'Outputs'
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    data_warehouse = path + os.sep + 'AD/data_warehouse'
    region = 'AT312'
    start_year = 2018
    last_year = 2030
    depr_time = 20
    dh_connection_rate_1st_year = 0.36
    dh_connection_rate_last_year = 0.5
    interest_rate = 0.05
    grid_cost = 25
    accumulated_energy_saving = 0.1
    inShapefile = data_warehouse + os.sep + region + '.shp'
    case_study = [inShapefile, start_year, last_year, depr_time,
                  accumulated_energy_saving, dh_connection_rate_1st_year,
                  dh_connection_rate_last_year, interest_rate, grid_cost]
    output_dir = path + os.sep + 'Outputs/' + str(grid_cost)+'_'+str(dh_connection_rate_last_year)+'_'+str(accumulated_energy_saving)
    output_summary = execute(case_study, output_dir)
    print(output_summary)
    elapsed = time.time() - start
    print('Sum of elapsed Time: %0.2f' % elapsed)
