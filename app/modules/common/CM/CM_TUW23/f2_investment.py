import os
import sys
import numpy as np
from osgeo import gdal
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.
                                                       abspath(__file__))))
if path not in sys.path:
    sys.path.append(path)
from CM.CM_TUW0.rem_mk_dir import rm_file
from CM.CM_TUW19 import run_cm as CM19


def annuity(r, period):
    return ((1+r)**period - 1) / (r*(1+r)**period)


def cost_factors(c1, c2, PR):
    PR_park = (PR < 0.3).astype(int)
    PR_outercity = (PR >= 0.3).astype(int) * (PR < 0.5).astype(int)
    PR_innercity = (PR >= 0.5).astype(int)
    cf1 = c1[0] * PR_park + c1[1] * PR_outercity + c1[2] * PR_innercity
    cf2 = c2[0] * PR_park + c2[1] * PR_outercity + c2[2] * PR_innercity
    del PR_park, PR_outercity, PR_innercity
    return cf1, cf2


def dh_demand(c1, c2, raster_plotratio, raster_hdm, start_year, last_year,
              accumulated_energy_saving, dh_connection_rate_1st_year,
              dh_connection_rate_last_year, depr_period, output_dir, interest,
              output_layers, dA_slope=0.0486, dA_intercept=0.0007,
              dataType='float32'):
    '''
    Important Note:
    1) Here, for the calculation of plot ratio, I used gross floor area raster
    in one hectar resolution (unit: m2). It should be divided by 1e4 to get the
    plot ratio.
    2) if you have plot ratio raster, remove the 1e4 factor.
    3) Distribution cost is calculated for those pixel that their corresponding
    pipe diameter is equal or greater than 0.
    the input heat density map should be in GWh/km2.
    '''
    horizon = last_year - start_year + 1
    if horizon > depr_period:
        raise Warning('Study horizon is longer than depr_period of district. '
                      'The calculation will be done only till the end of '
                      'depr_period!')
        horizon = depr_period
        remaining_years = 0
    else:
        remaining_years = depr_period - horizon

    energy_reduction_factor = (1-accumulated_energy_saving)**(1/(horizon-1))
    hdm_ds = gdal.Open(raster_hdm)
    hdm_band = hdm_ds.GetRasterBand(1)
    hdm = hdm_band.ReadAsArray().astype(float)
    geo_transform = hdm_ds.GetGeoTransform()
    plotRatio_ds = gdal.Open(raster_plotratio)
    plotRatio_band = plotRatio_ds.GetRasterBand(1)
    # gfa in hectar should be devided by 10000 to get right values for
    # plot ratio (m2/m2).
    plotRatio = plotRatio_band.ReadAsArray().astype(float)/10000.0
    hdm_ds = plotRatio_ds = None
    row, col = np.nonzero((hdm > 0).astype(int) * (plotRatio > 0.0).astype(int))
    # unit conversion from MWh/ha to GJ/m2
    sparseDemand = 0.00036*hdm[row, col]
    PR_sparse = plotRatio[row, col]
    # the unit for L is m/m2
    # L is in m/m2: to get the value for each pixel (ha) you should multiply it
    # by 10000 because 1 pixel has 10000 m2
    L = 1/(61.8 * PR_sparse**(-0.15))
    # initialize the variables
    q = 0
    # q_new = dh_connection_rate_1st_year * sparseDemand
    q_tot = np.copy(sparseDemand)
    q_max = np.zeros_like(q_tot)
    for i in range(horizon):
        q_tot = sparseDemand * energy_reduction_factor**i
        q_new = q_tot * (dh_connection_rate_1st_year + i * (dh_connection_rate_last_year - dh_connection_rate_1st_year)/(horizon-1))
        # q_new is a non-zero sparse matrix. The development of demand can be
        # checked by comparing just one element of q_new with q_max.
        if q_new[0] > q_max[0]:
            q_max = np.copy(q_new)
        q += q_new / (1 + interest)**i
    if remaining_years > 0:
        alpha_horizon = annuity(interest, horizon-1)
        alpha_depr = annuity(interest, depr_period)
        rest_annuity_factor = alpha_depr - alpha_horizon
        q = q + q_new * rest_annuity_factor
    linearHeatDensity = q_max / L
    # this step is performed to avoid negative effective pipe diameter
    LHD_THRESHOLD = -dA_intercept/dA_slope
    filtered_LHD = (np.log(linearHeatDensity) < LHD_THRESHOLD).astype(int)
    elements = np.nonzero(filtered_LHD)[0]
    dA = dA_slope * (np.log(linearHeatDensity)) + dA_slope
    cf1, cf2 = cost_factors(c1, c2, PR_sparse)
    dA[elements] = 0
    q_max[elements] = 0
    denominator = q / L
    divisor = cf1[1] + cf2[1]*dA
    divisor[elements] = 0
    investment = divisor/denominator
    finalInvestment = np.zeros_like(hdm, dtype=dataType)
    # from Euro/GJ/m2 to Euro/MWh/m2
    finalInvestment[row, col] = investment*3.6
    maxDHdem_arr = np.zeros_like(finalInvestment, dtype=dataType)
    # max DH demand density in MWh within the study horizon
    maxDHdem_arr[row, col] = q_max*10000/3.6

    invest_Euro_arr = maxDHdem_arr * finalInvestment
    hdm_last_year = np.zeros_like(finalInvestment, dtype=dataType)
    # total demand in the last year of study horizon in MWh/ha
    hdm_last_year[row, col] = q_tot*10000/3.6
    # total demand in last year in GWh for pixels with Plot Ration > 0
    last_year_dem = np.sum(hdm_last_year)/1000
    # Length of pipes (L)
    length = np.zeros_like(finalInvestment, dtype=dataType)
    length[row, col] = L
    length[row, col][elements] = 0
    maxDHdem, invest_Euro, hdm_cut_last_year, total_pipe_length = output_layers
    rm_file(maxDHdem, invest_Euro, hdm_cut_last_year, total_pipe_length)
    CM19.main(maxDHdem, geo_transform, dataType, maxDHdem_arr)
    CM19.main(invest_Euro, geo_transform, dataType, invest_Euro_arr)
    CM19.main(hdm_cut_last_year, geo_transform, dataType, hdm_last_year)
    CM19.main(total_pipe_length, geo_transform, dataType, length)
    # sum(MWh/ha) and convert to GWh
    first_year_dem_all = np.sum(hdm)/1000
    # demand in GWh for pixels with Plot Ratio > 0
    first_year_dem = np.sum(sparseDemand)*10000/3600
    return first_year_dem_all, first_year_dem, last_year_dem
