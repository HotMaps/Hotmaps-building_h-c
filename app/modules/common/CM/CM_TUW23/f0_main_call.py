import os
import sys
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)
import CM.CM_TUW24.run_cm as CM24
from CM.CM_TUW0.rem_mk_dir import rm_mk_dir, rm_dir, rm_file
from CM.CM_TUW23.f1_clip_to_selection import raster_cut
from CM.CM_TUW23.f2_investment import dh_demand
from CM.CM_TUW23.f3_coherent_areas import distribuition_costs
from CM.CM_TUW23.f4_pre_optimization import pre_opt
from CM.CM_TUW23.f9_results_summary import summary


def main(case_study, pixT, DHT, gfa_path, hdm_path, output_dir):
    # grid factor of 1.05 shows the ratio of total grid costs to distribtion
    # grid costs and is set based on previously run sensitivity analyses as
    # well as other studies in the literature.
    grid_factor = 1.05
    [inShapefile, start_year, last_year, depr_time, accumulated_energy_saving,
     dh_connection_rate_1st_year, dh_connection_rate_last_year,
     interest_rate, grid_cost] = case_study
    # c1 and c2 are based on Swedish experience and are taken from literature.
    c1 = [292.38, 218.78, 154.37]
    c2 = [2067.13, 1763.5, 1408.76]
    dist_grid_cost = grid_cost/grid_factor
    temp_dir = output_dir + os.sep + 'feat_layers'
    rm_mk_dir(output_dir, temp_dir)
    outShapefile = temp_dir + os.sep + 'F23_selected_area.shp'
    maxDHdem = output_dir + os.sep + 'F23_maxDHdem.tif'
    invest_Euro = output_dir + os.sep + 'F23_invest_Euro.tif'
    hdm_cut_last_year = output_dir + os.sep + 'F23_hdm_cut_last_year.tif'
    total_pipe_length = output_dir + os.sep + 'F23_tot_pipe_length.tif'
    coh_area_raster = output_dir + os.sep + 'F23_dh_reg_bool.tif'
    hdm_dh_reg_last_year = output_dir + os.sep + 'F23_hdm_dh_reg_last_year.tif'
    label_raster = output_dir + os.sep + 'F23_label.tif'
    outPolygon = output_dir + os.sep + 'F23_prelabel.shp'
    sol_csv = output_dir + os.sep + 'solution.csv'
    CM24.main(inShapefile, outShapefile, 3035)
    # f1: cut the hdm and plot ration rasters to the selected region
    hdm_cut_first_year = raster_cut(hdm_path, outShapefile, output_dir, 'F23_hdm_cut')
    gfa_cut_first_year = raster_cut(gfa_path, outShapefile, output_dir, 'F23_gfa_cut')
    # f2: calculate pixel based values
    f2_output_layers = [maxDHdem, invest_Euro, hdm_cut_last_year,
                        total_pipe_length]
    first_year_dem_all, first_year_dem, last_year_dem = dh_demand(c1, c2,
                    gfa_cut_first_year, hdm_cut_first_year, start_year, last_year,
                    accumulated_energy_saving, dh_connection_rate_1st_year,
                    dh_connection_rate_last_year, depr_time, output_dir,
                    interest_rate, f2_output_layers)
    # f3: Determination of coherent areas based on the grid cost threshold.
    distribuition_costs(invest_Euro, maxDHdem, outShapefile,
                        hdm_cut_first_year, hdm_cut_last_year,
                        dh_connection_rate_1st_year, pixT, DHT, dist_grid_cost,
                        coh_area_raster, hdm_dh_reg_last_year, label_raster)
    # f4: pre-steps for providing input to the optimization function including
    # calling various functions for calculating distance between coherent
    # areas, optimization module, illustrating the transmission lines,
    # polygonize the coherent areas.
    (covered_demand, dist_inv, dist_spec_cost, trans_inv, trans_spec_cost,
     trans_line_length), dist_pipe_len, heat_dem_1st, \
     heat_dem_last, n_coh_areas, \
     n_coh_areas_selected = pre_opt(coh_area_raster, grid_cost, output_dir,
                                    hdm_cut_first_year, hdm_cut_last_year,
                                    total_pipe_length, maxDHdem, outShapefile,
                                    label_raster, invest_Euro, outPolygon,
                                    depr_time, interest_rate, sol_csv,
                                    polygonize_region=True)
    # f8: returns the summary of results in a dictionary format
    output_summary = summary(covered_demand, dist_inv, dist_spec_cost,
                             trans_inv, trans_spec_cost, trans_line_length,
                             dist_pipe_len, heat_dem_1st, heat_dem_last,
                             n_coh_areas, n_coh_areas_selected)
    rm_dir(temp_dir)
    rm_file(maxDHdem, invest_Euro, hdm_cut_first_year, hdm_cut_last_year,
            coh_area_raster, label_raster, hdm_dh_reg_last_year,
            gfa_cut_first_year, maxDHdem[:-4]+'.tfw', invest_Euro[:-4]+'.tfw',
            hdm_cut_first_year[:-4]+'.tfw', hdm_cut_last_year[:-4]+'.tfw',
            coh_area_raster[:-4]+'.tfw', label_raster[:-4]+'.tfw',
            hdm_dh_reg_last_year[:-4]+'.tfw', gfa_cut_first_year[:-4]+'.tfw')
    return output_summary
