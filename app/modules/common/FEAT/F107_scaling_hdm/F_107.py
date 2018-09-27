import os
import sys
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)
import CM.CM_TUW18.run_cm as CM18
import CM.CM_TUW19.run_cm as CM19
import CM.CM_TUW22.run_cm as CM22
from AD.F107.main import ad_f107


def execute(updated_demand_value, output_dir):
    '''
    updated_demand_value in GWh/a
    '''
    selected_area, hdm_path = ad_f107()
    outRasterPath = output_dir + os.sep + 'F107_hdm_cut_scaled.tif'
    CM18.main(hdm_path, selected_area, updated_demand_value, output_dir,
              outRasterPath)
    return {'F107_out_raster_path_0': outRasterPath}


if __name__ == "__main__":
    output_dir = path + os.sep + 'Outputs'
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    # updated demand in GWh/a
    updated_demand_value = 6000
    output = execute(updated_demand_value, output_dir)
    print(output)
