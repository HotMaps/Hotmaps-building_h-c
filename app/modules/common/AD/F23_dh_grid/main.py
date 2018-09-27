import numpy as np
import os
import sys
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)
from AD.heat_density_map.main import HDMAP


def ad_f23():
    path = os.path.dirname(os.path.dirname(__file__))
    # pixT in MWh/ha
    pixT = 10*np.arange(1, 135, 0.1)
    # DHT in GWh/year just for filtering the low demand pixels out.
    DHT = 1
    data_warehouse = path + os.sep + 'data_warehouse'
    hdm_path = HDMAP(data_warehouse)
    gfa_path = data_warehouse + os.sep + 'gfa_tot_curr_density_AT.tif'
    available_data = (pixT, DHT, gfa_path, hdm_path)
    return available_data


if __name__ == '__main__':
    output = ad_f23()
    print(output)
