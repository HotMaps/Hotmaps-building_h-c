import os
import sys
import networkx as nx
import numpy as np
import pandas as pd
from scipy.ndimage import measurements
#from scipy.sparse import csr_matrix
#from scipy.sparse.csgraph import minimum_spanning_tree
#from scipy.spatial.distance import cdist
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)
import CM.CM_TUW4.run_cm as CM4
from CM.CM_TUW0.rem_mk_dir import rm_mk_dir
from CM.CM_TUW1.read_raster import raster_array
from CM.CM_TUW23.f5_distance_calculation import feature_dist
from CM.CM_TUW23.f6_optimization import optimize_dist
from CM.CM_TUW23.f7_polygonize import polygonize as poly
from CM.CM_TUW23.f8_show_in_graph import edge_representation


def pre_opt(coh_area_raster, grid_cost, output_dir, hdm_1st, hdm_last,
            total_pipe_length, maxDHdem_path, inShapefile, label_raster,
            invest_Euro, outPolygon, depr_time, r, sol_csv, epsg=3035,
            struct=np.ones((3, 3)), polygonize_region=False,
            full_load_hours=3000):
    '''
    ########################################################
    edge_folder_name = inShapefile.split('/')[-1][:-4]
    edge_folder_name = 'edges'
    edge_folder = output_dir + os.sep + edge_folder_name
    rm_mk_dir(edge_folder)
    ########################################################
    '''
    hdm_arr, geoTrans = raster_array(hdm_last, return_gt=True)
    labels = raster_array(label_raster, 'int16')
    nr_coherent = np.max(labels)
    labels_copy = np.copy(labels)
    distance_matrix, row_from_label, col_from_label, \
        row_to_label, col_to_label = feature_dist(labels)
    '''
    # in case of center-to-center distance use the following:
    distance_matrix = 100 * cdist(coords, coords, 'euclidean')
    '''
    ###########################################################################
    ###########################################################################
    total_pipe_length_arr = raster_array(total_pipe_length)
    hdm_1st_arr = raster_array(hdm_1st)
    dist_invest_arr = raster_array(invest_Euro)
    maxDHdem_arr = raster_array(maxDHdem_path)
    # prepare dataframe for final answers
    heat_dem_coh_1st = np.zeros((nr_coherent))
    heat_dem_coh_last = np.zeros((nr_coherent))
    heat_dem_spec_area = np.zeros((nr_coherent))
    dist_pipe_len = np.zeros((nr_coherent))
    q = np.zeros((nr_coherent))
    q_inv = np.zeros((nr_coherent))
    q_spec_cost = np.zeros((nr_coherent))
    area_coh_area = np.zeros((nr_coherent))
    for i in range(1, nr_coherent+1):
        j = i-1
        temp = labels_copy == i
        # in hectare
        area_coh_area[j] = np.sum(temp)
        heat_dem_coh_1st[j] = np.sum(hdm_1st_arr[temp])
        heat_dem_coh_last[j] = np.sum(hdm_arr[temp])
        # pipe length raster is in m/m2 and for each pixel needs a factor 10000
        # for meter and factor 1e-3 for km. Overal factor 10 to get it in km
        dist_pipe_len[j] = np.sum(total_pipe_length_arr[temp])*10
        q[j] = np.sum(maxDHdem_arr[temp])
        q_inv[j] = np.sum(dist_invest_arr[temp])
        q_spec_cost[j] = q_inv[j] / q[j]
        # MWh/km2
        heat_dem_spec_area[j] = heat_dem_coh_last[j] / area_coh_area[j]
    df = pd.DataFrame({
                       'heat demand total 1st year [MWh]': heat_dem_coh_1st,
                       'heat demand total last year [MWh]': heat_dem_coh_last,
                       'potential heat demand district heating [MWh]': q,
                       'specific heat demand total 1st year [MWh/km2]': heat_dem_spec_area,
                       'distribution line length [km]': dist_pipe_len,
                       'distribution costs [EUR]': q_inv,
                       'distribution costs [EUR/MWh]': q_spec_cost,
                       'area [km2]': area_coh_area
                       })
    '''
    Dimension DN Water flow m/s Capacity MW Cost EUR/m
    Reference: GIS based analysis of future district heating in Denmark
    Author: Steffan Nielsen, Bernd Moeller

    Important Note: this is a simplified method for finding the diameter of the
    transmission lines. The capacity and therefore, the cost of a transmission
    line is set only considering two coherent areas.
    for calculation of the cost, 3000h of full load hours has been considered.
    '''
    annuity_factor = (r*(1+r)**depr_time)/((1+r)**depr_time-1)
    # power[MW], transmission line cost[EUR/m]
    tl_cost = np.array([[0, 0], [0.2, 195], [0.3, 206], [0.6, 220], [1.2, 240],
                        [1.9, 261], [3.6, 288], [6.1, 323], [9.8, 357],
                        [20,  426], [45,  564], [75,  701], [125, 839],
                        [190, 976], [19000, 97600]])
    
    tl_cost_copy = np.copy(tl_cost)
    temp_q = np.copy(q)
    power_to_add = temp_q[temp_q/full_load_hours > 190]/full_load_hours
    for item in power_to_add:
        for i in range(1, 5):
            temp_price = i * item / 190 * 976
            tl_cost_copy = np.concatenate((tl_cost_copy, [[i * item, temp_price]]))
        '''
        for i in range(tl_cost.shape[0]):
            temp_pow = (item + tl_cost[i, 0])/2
            temp_price = temp_pow / 190 * 976
            tl_cost_copy = np.concatenate((tl_cost_copy, [[temp_pow, temp_price]]))
        '''
    tl_cost_copy = tl_cost_copy[tl_cost_copy[:, 0].argsort()]
    tl_cost = np.copy(tl_cost_copy)

    # consideration of annuity factor
    tl_cost[:, 1] = tl_cost[:, 1] * annuity_factor

    # term_cond, dh_filtered, edge_list_filtered = optimize_dist(grid_cost, distance_matrix_filtered, trans_line_cost_filtered, q_filtered, q_spec_cost_filtered)
    cost_matrix = tl_cost[:, 1]
    pow_range_matrix = tl_cost[:, 0]
    term_cond, dh, edge_list = optimize_dist(grid_cost, cost_matrix,
                                             pow_range_matrix,
                                             distance_matrix, q, q_spec_cost)
    grid_cost_header = 'Connected at %0.2f EUR/MWh' % grid_cost
    df[grid_cost_header] = dh[:-6]
    df['label'] = df.index + 1
    headers = ['label', 'heat demand total 1st year [MWh]',
               'heat demand total last year [MWh]',
               'potential heat demand district heating [MWh]',
               'distribution costs [EUR/MWh]',
               'specific heat demand total 1st year [MWh/km2]',
               'distribution costs [EUR]', 'area [km2]',
               'distribution line length [km]', grid_cost_header]
    df = df[headers]
    df.to_csv(sol_csv)
    if polygonize_region and term_cond:
        economic = dh[:-6]
        poly(coh_area_raster, label_raster, outPolygon, economic,
             heat_dem_coh_last, heat_dem_spec_area, q, q_spec_cost,
             area_coh_area)
    node_label_list = np.arange(1, nr_coherent+1) * dh[0: -6]
    if term_cond:
        if len(edge_list) > 0:
            edge_folder = output_dir + os.sep + 'edges'
            edge_representation(row_from_label, col_from_label, row_to_label,
                                col_to_label, distance_matrix, node_label_list,
                                edge_list, geoTrans, edge_folder)
            # for the case center-to-center use the follwoing line instead!
            # edge_representation(label_raster, coords, distance_matrix,
            #                     node_label_list, edge_list,
            #                     edge_folder + os.sep + str(grid_cost))
        
        
    '''
    #########################################################################
    #########################################################################
    node_label_list = np.arange(1, nr_coherent+1) * dh[0: -6]
    if term_cond:
        if len(edge_list) > 0:
            edge_folder = output_dir + os.sep + 'edges'
            edge_representation_old(label_raster, coh_area_raster, distance_matrix,
                                node_label_list, edge_list, edge_folder)
            # for the case center-to-center use the follwoing line instead!
            # edge_representation(label_raster, coords, distance_matrix,
            #                     node_label_list, edge_list,
            #                     edge_folder + os.sep + str(grid_cost))
    #########################################################################
    #########################################################################
    '''
    sum_dist_pipeline = np.sum(dist_pipe_len * dh[:-6])
    calculated_total_trans_cost = 0
    return dh[-6:], sum_dist_pipeline, np.sum(hdm_1st_arr), np.sum(hdm_arr), nr_coherent, np.sum(dh[:-6])
