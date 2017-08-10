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


def execute(updated_demand_value, output_dir, outRasterPath):
    #
    selected_area, hdm = ad_f107()
    hdm_cut, geo_transform = CM22.main(hdm, selected_area, output_dir,
                                       nodata=0, return_array=True)
    new_HDM_cut = CM18.main(hdm_cut, updated_demand_value)
    CM19.main(outRasterPath, geo_transform, "float32", new_HDM_cut)
    return {'path': outRasterPath}


if __name__ == "__main__":
    #print('Calculation started!')
    # path to the src
    output_dir = path + os.sep + 'Outputs'
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    # updated demand in GWh/a
    updated_demand_value = 6000
    outRasterPath = output_dir + os.sep + 'F107_' + 'scaled_hdm.tif'
    output = execute(updated_demand_value, output_dir, outRasterPath)
    #print('Calculation ended successfully!')
