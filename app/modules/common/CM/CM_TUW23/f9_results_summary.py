from collections import OrderedDict
import os
import sys
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)


def summary(covered_demand, dist_inv, dist_spec_cost, trans_inv,
            trans_spec_cost, trans_line_length, dist_pipe_length, heat_dem_1st,
            heat_dem_last, n_coh_areas, n_coh_areas_selected):
    summary = OrderedDict()
    summary['Total demand in selected region in the first year of investment [MWh]'] = heat_dem_1st
    summary['Total demand in selected region in the last year of investment [MWh]'] = heat_dem_last
    summary['District heat demand [MWh]'] = covered_demand
    summary['Specific grid costs [EUR/MWh]'] = dist_spec_cost + trans_spec_cost
    summary['Specific distribution grid costs [EUR/MWh]'] = dist_spec_cost
    summary['Specific transmission grid costs [EUR/MWh]'] = trans_spec_cost
    summary['Distribution grid costs per meter [EUR/m]'] = dist_inv/(dist_pipe_length*1000 + 1)
    summary['Transmission grid costs per meter [EUR/m]'] = trans_inv/(trans_line_length*1000 + 1)
    summary['Grid costs [EUR]'] = dist_inv + trans_inv
    summary['Total distribution grid costs [EUR]'] = dist_inv
    summary['Total transmission grid costs [EUR]'] = trans_inv
    summary['Distribution line length [km]'] = dist_pipe_length
    summary['Transmission line length [km]'] = trans_line_length
    summary['Total number of coherent areas'] = n_coh_areas
    summary['Number of selected coherent areas'] = n_coh_areas_selected
    return summary
