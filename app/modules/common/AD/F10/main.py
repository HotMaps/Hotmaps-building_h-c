import os
import sys
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)


def ad_f10():
    data_warehouse = path + '/AD/data_warehouse'
    file_names = {'tech_info_sheet': '/AD.ISI.h&c_technologies_EU28.csv',
                  'load_factor_sheet': '/AD.TUW2_120%max_load_factor.csv',
                  'energy_price_sheet': '/AD.TUW2_dummy_fuel_costs.csv',
                  'specific_demand_sheet': '/AD.EURAC.Ave_useful_h&c_demand.csv'}
    _tech_info_sheet = data_warehouse + file_names['tech_info_sheet']
    _load_factor_sheet = data_warehouse + file_names['load_factor_sheet']
    _energy_price_sheet = data_warehouse + file_names['energy_price_sheet']
    _specific_demand_sheet = data_warehouse + file_names['specific_demand_sheet']
    for item in file_names.keys():
        file_path = data_warehouse + file_names[item]
        if not os.path.exists(file_path):
            raise Exception('The \"' + item + '\" cannot be found in the database!')
    return _tech_info_sheet, _load_factor_sheet, _energy_price_sheet, _specific_demand_sheet
