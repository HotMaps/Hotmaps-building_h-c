import os
import sys
import numpy as np
from scipy.ndimage import measurements
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)
from CM.CM_TUW0.rem_mk_dir import rm_file
from CM.CM_TUW1.read_raster import raster_array
from CM.CM_TUW4 import run_cm as CM4
from CM.CM_TUW19 import run_cm as CM19


def distribuition_costs(invest_Euro, maxDHdem, features_path, hdm_1st, hdm_last, MS_1st,  pixT,
                        DHT, costT, coh_area_raster, hdm_dh_reg_last_year,
                        label_raster, struct=np.ones((3, 3))):
    rm_file(coh_area_raster, hdm_dh_reg_last_year, label_raster)
    invest_Euro_arr = raster_array(invest_Euro)
    maxDHdem_arr = raster_array(maxDHdem)
    hdm_arr, geo_transform = raster_array(hdm_last, return_gt=True)
    rast_origin = geo_transform[0], geo_transform[3]
    coh_areas = np.zeros_like(maxDHdem_arr, 'int8')
    reg_filter = maxDHdem_arr.astype(bool).astype('int8')
    for pix_threshold in pixT:
        # calculate coherent regions with given thresholds and cut them to
        # LAU2 levels
        DH_Regions = CM4.main(hdm_arr, features_path, pix_threshold, DHT,
                              None, rast_origin, only_return_areas=True)
        # multiplication with reg_filter required to follow maxDHdem
        # pattern and separate connection of regions with pixels that have
        # value of zero in maxDHdem
        result = DH_Regions.astype(int) * reg_filter
        labels, nr_coherent = measurements.label(result, structure=struct)
        if nr_coherent == 0:
            break
        for i in range(1, nr_coherent+1):
            temp = labels == i
            q = np.sum(maxDHdem_arr[temp])
            q_inv = np.sum(invest_Euro_arr[temp])
            q_spec_cost = q_inv / q
            if q_spec_cost <= costT and q >= DHT:
                coh_areas[temp] = 1
                hdm_arr[temp] = 0
        labels = None 
        nr_coherent = None
    hdm_last_arr = raster_array(hdm_last)
    hdm_1st_arr = raster_array(hdm_1st)
    labels, numLabels = measurements.label(coh_areas, structure=struct)
    if numLabels == 0:
        raise ValueError('For the provided grid cost ceiling, no district '
                         'heating potential area can be realized!')
    if numLabels > 100:
        raise ValueError('For the given scenario, we found more than 100 '
                         'coherent areas. Please reduce the size of your '
                         'selection and run the scenario again!')
    hdm_in_dh_reg = hdm_last_arr * coh_areas
    CM19.main(coh_area_raster, geo_transform, 'int8', coh_areas)
    CM19.main(hdm_dh_reg_last_year, geo_transform, "float64", hdm_in_dh_reg)
    CM19.main(label_raster, geo_transform, "int16", labels)
    # average demand in dh regions: sum_demand/sum_area_of_dhReg
    # MWh/ha
    ave_dem_dh_reg = np.sum(hdm_in_dh_reg) / np.sum(coh_areas)
