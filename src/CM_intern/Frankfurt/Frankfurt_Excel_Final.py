import time
import pandas as pd
import numpy as np


def demand_calc(inCSV1, inCSV2, inCSV3, outputCSV):
    constant_ave_res_KGF = 223.6
    spec_dem_res = [0, 219, 212, 205, 134, 189, 177, 220, 269, 253, 144, 157, 311, 311]
    spec_dem_res_KGF = [0, 173, 0, 0, 0, 189, 177, 220, 269, 253, 144, 157, 311, 311]
    
    
    ifile0 = pd.read_csv(inCSV1)
    ifile1 = ifile0.sort_values(["ID"])
    ifile2 = pd.read_csv(inCSV2) # KGF to GArt
    ifile3 = pd.read_csv(inCSV3) # districts' specific demand + KGF averages
    check_null = ifile1.notnull().values
    inCSV1_cols = ifile1.columns.tolist()
    ifile1_val = ifile1.values
    ifile3_val = ifile3.values
    
    KGF_categories = ifile2['KGF'].values
    KGF_corresponding_GArt = ifile2['GArt'].values
    dict_KGF2GArt = dict(zip(KGF_categories,KGF_corresponding_GArt))
    
    
    specific_demand_res = ifile3.values
    district = ifile3['District'].values
    districtIndex = np.arange(district.size)
    dict_dist_demand = dict(zip(district,districtIndex))
    
    
    ID = ifile1['ID'].values.astype(int)
    GArt =ifile1['GArt'].values
    KGF =ifile1['KGF'].values
    Footprint_SHP = ifile1['Footprint_SHP'].values
    NrFloor_SHP = ifile1['NrFloor_SHP'].values 
    Footprint_Access = ifile1['Footprint_Access'].values
    NrFloor_Access = ifile1['NrFloor_Access'].values
    Footprint_Access_index = inCSV1_cols.index('Footprint_Access')
    NrFloor_Access_index = inCSV1_cols.index('NrFloor_Access')
    Stadtbezirk_Nr_index = inCSV1_cols.index('Stadtbezirk_Nr')
    Stadtbezirk_Own_SHP_index = inCSV1_cols.index('Stadtbezirk_Own_SHP')
    GIndex_Access_index = inCSV1_cols.index('GIndex_Access')
    Orig_Sepc_Demand_Access_index = inCSV1_cols.index('Orig_Spec_Demand_Access')
    Sepc_Demand_Access_index = inCSV1_cols.index('Spec_Demand_Access')
   
    x = np.empty((len(ID), 10)) * np.nan
    for i in range(len(ID)):
        # KGF to GArt categories
        x[i, 0] = dict_KGF2GArt[KGF[i]]
        # Gross floor area of SHP
        x[i, 1] = NrFloor_SHP[i] * Footprint_SHP[i]
        # Gross floor area of Access matches &&&&& Orig_Dem_Access &&&&& Dem_Access
        if check_null[i, Footprint_Access_index] and check_null[i, NrFloor_Access_index]:
            x[i, 2] =  Footprint_Access[i] * NrFloor_Access[i]
            x[i, 7] =  x[i, 2] * ifile1_val[i, Orig_Sepc_Demand_Access_index]
            x[i, 9] =  x[i, 2] * ifile1_val[i, Sepc_Demand_Access_index]
        # Orig_Spec_Dem_KGF
        if x[i, 0] == 1 and GArt[i] > 0 and GArt[i] < 5:
            x[i, 3] =  spec_dem_res[GArt[i]]
        else:
            x[i, 3] =  spec_dem_res_KGF[int(x[i, 0])]
        # Spec_Dem_KGF
        if check_null[i, Stadtbezirk_Own_SHP_index]:
            if x[i, 0] == 1 and GArt[i] > 0 and GArt[i] < 5:
                # 1 + GArt[i]: because the first col is district, 2: KGF averages
                x[i, 4] = ifile3_val[dict_dist_demand[ifile1_val[i, Stadtbezirk_Own_SHP_index]], 1 + GArt[i]]
            else:
                x[i, 4] = ifile3_val[dict_dist_demand[ifile1_val[i, Stadtbezirk_Own_SHP_index]], 1]
        elif check_null[i, Stadtbezirk_Nr_index]:
            if x[i, 0] == 1 and GArt[i] > 0 and GArt[i] < 5:
                # 1 + GArt[i]: because the first col is district, 2: KGF averages
                x[i, 4] = ifile3_val[dict_dist_demand[ifile1_val[i, Stadtbezirk_Nr_index]], 1 + GArt[i]]
            else:
                x[i, 4] = ifile3_val[dict_dist_demand[ifile1_val[i, Stadtbezirk_Nr_index]], 1]
        else:
            x[i, 4] = constant_ave_res_KGF
        # Orig_Dem_KGF
        x[i, 5] = x[i, 3] * x[i, 1]
        # Orig_Dem_KGF_with_match
        if check_null[i, GIndex_Access_index]:
            x[i, 6] = x[i, 4] * x[i, 1]
        # Dem_KGF
        x[i, 8] = x[i, 4] * x[i, 1]
        # Dem_KGF_with_match
    
    
    ifile1['KGF2GArt'] = x[:, 0]
    ifile1['GFA_SHP'] = x[:, 1]
    ifile1['GFA_Access'] = x[:, 2]
    ifile1['Orig_Spec_Dem_KGF'] = x[:, 3]
    ifile1['Spec_Dem_KGF'] = x[:, 4]
    ifile1['Orig_Dem_KGF'] = x[:, 5]
    ifile1['Orig_Dem_KGF_with_match'] = x[:, 6]
    ifile1['Orig_Dem_Access'] = x[:, 7]
    ifile1['Dem_KGF'] = x[:, 8]
    ifile1['Dem_Access'] = x[:, 9]
    
    ifile1 = ifile1.sort_values(["ID"])
    ifile1.to_csv(outputCSV)
    
    
if __name__ == "__main__":
    start = time.time()
    inCSV1 = "/home/simulant/ag_lukas/personen/Mostafa/Frankfurt Buildingblocks/Excel_Calc/Frankfurt.csv"
    inCSV2 = "/home/simulant/ag_lukas/personen/Mostafa/Frankfurt Buildingblocks/Excel_Calc/KGF2GArt.csv"
    inCSV3 = "/home/simulant/ag_lukas/personen/Mostafa/Frankfurt Buildingblocks/Excel_Calc/Spec_Dem.csv"
    outputCSV = "/home/simulant/ag_lukas/personen/Mostafa/Frankfurt Buildingblocks/Excel_Calc/test_result.csv"
    demand_calc(inCSV1, inCSV2, inCSV3, outputCSV)
    print(time.time() - start)    
    
    