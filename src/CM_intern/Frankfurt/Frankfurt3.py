import time
import re
import pandas as pd
import numpy as np


def match(inputCSV1, inputCSV2, inputCSV3, specificDemand, outputCSV):
    # Building demand based on type [GWh/m2/a]
    # Frankfurt has no data regarding age of the building. In case such data exist
    # it should be considered in calculation.
    # demand types: 0: no demand; 1: einzelhaus; 2: Doppelhaus, 3: Reihenhaus; 4: Mehrfamilienhaus; 5:Mischnutzung; 6: Buero
    # 7: Gewerbe; 8 Beherbergung; 9: Gastronomie; 10:oeffentliches Gebaeude; 11: Schule; 12: Krankenhaus; 13: Schwimmbad
    demand_typ = np.array([0, 219, 212, 205, 134, 189, 177, 220, 269, 253,
                           144, 157, 311, 311]) * 0.000001
    # Building types based on the category provided in the shapefile. This 
    # category is used for those entries that do not exist in the Access database.
    dict_typ_conv = {
                "1000.0":1, "1020.0":8, "1022.0":8, "1100.0":5, "1120.0":5, "1223.0":8,
                "2010.0":7, "2020.0":6, "2030.0":10, "2040.0":6, "2051.0":7, "2052.0":7,
                "2053.0":7, "2055.0":7, "2056.0":7, "2060.0":10, "2070.0":8, "2071.0":8,
                "2074.0":8, "2081.0":9, "2090.0":10, "2092.0":10, "2100.0":7, "2130.0":0,
                "2320.0":5, "2410.0":5, "2420.0":5, "2430.0":5, "2431.0":5, "2443.0":5,
                "2460.0":0, "2461.0":0, "2462.0":0, "2463.0":0, "2465.0":0, "2501.0":0,
                "2510.0":5, "2511.0":5, "2513.0":0, "2520.0":0, "2522.0":0, "2523.0":0,
                "2540.0":6, "2570.0":0, "2580.0":5, "2620.0":0, "2700.0":5, "2721.0":0,
                "2723.0":0, "2740.0":5, "3010.0":6, "3012.0":10, "3013.0":10, "3014.0":10,
                "3015.0":10, "3016.0":10, "3020.0":11, "3021.0":11, "3022.0":11, "3023.0":11,
                "3024.0":11, "3030.0":11, "3031.0":10, "3032.0":10, "3033.0":10, "3034.0":10,
                "3035.0":6, "3036.0":10, "3037.0":10, "3040.0":10, "3041.0":10, "3042.0":10,
                "3044.0":10, "3045.0":10, "3046.0":10, "3047.0":10, "3048.0":10, "3050.0":12,
                "3051.0":12, "3052.0":12, "3060.0":10, "3061.0":8, "3062.0":8, "3065.0":11,
                "3070.0":10, "3071.0":6, "3072.0":6, "3073.0":8, "3074.0":0, "3075.0":8,
                "3080.0":0, "3081.0":10, "3082.0":0, "3091.0":10, "3092.0":10, "3094.0":10,
                "3095.0":10, "3097.0":6, "3211.0":10, "3221.0":13, "3222.0":13, "3230.0":6,
                "3260.0":6, "3270.0":6, "3290.0":10, "11491.0":8, "13074.0":0, "19950.0":0,
                "19951.0":0, "19952.0":0, "19953.0":10}
    areaThresholdList1 = 0.20 * np.arange(1,26)
    areaThresholdList2 = np.arange(6,30)
    areaThresholdList = np.concatenate((areaThresholdList1, areaThresholdList2))
    maxIndex_areaThresholdList = areaThresholdList.size - 1
   
    ############################################################################
    spec_dem_res = pd.read_csv(specificDemand)
    specific_demand_res = spec_dem_res.values
    district = spec_dem_res['District'].values
    districtIndex = np.arange(district.size)
    dict_dist_demand = dict(zip(district,districtIndex))
    ############################################################################
    # Access building blocks
    ifile1 = pd.read_csv(inputCSV1).astype('str')
    ifile1 = ifile1.sort_values(["STRASSENKENNZIFFER","HAUSNUMMER"])
    Strvrz1 = ifile1['STRASSENKENNZIFFER'].values
    HausNr1 = ifile1['HAUSNUMMER'].values.tolist()
    footprint1 = ifile1['FLAECHE'].values.astype(float)
    FloorNr1 = ifile1['STOCKWERKSZAHL'].values
    GINDEX1 = ifile1['GINDEX'].values
    GEBAEUDEART1 = ifile1['GEBAEUDEART'].values
    HausNrTemp = []
    for item in HausNr1:
        HausNrTemp.append("".join(item.split()))
        #HausNrTemp.append(item.replace(" ",""))
    HausNr = np.array(HausNrTemp)  
    obj1 = Strvrz1 + ' ' + HausNr
    ############################################################################
    # CSV from the shapefile
    ifile2 = pd.read_csv(inputCSV2)
    ID = ifile2['ID'].values.tolist()
    Footprint = ifile2['Footprint'].values.astype(float).tolist()
    OBJ = ifile2['OBJ'].values.astype(str).tolist()
    KGF = ifile2['KGF'].values.astype(int)
    GFA = ifile2['GFA'].values.astype(float)
    IDLength = len(ID)
    FloorNr_Access = np.nan * np.empty(IDLength)
    GIndex_Access = np.nan * np.empty(IDLength)
    Footprint_Access = np.nan * np.empty(IDLength)
    GArt = np.ones(IDLength).astype(int)*99999
    GArt_KGF = np.ones(IDLength).astype(int)*99999
    ############################################################################
    # Access Streets, House Number, district
    ifile3 = pd.read_csv(inputCSV3)
    strNr = ifile3['strNr'].values.astype(int)
    Nr_from = ifile3['Nr_from'].tolist()
    add1 = ifile3['add1'].values.tolist()
    Nr_to = ifile3['Nr_to'].values.tolist()
    add2 = ifile3['add2'].values.tolist()
    Ortsbezirk_Nr3 = ifile3['Ortsbezirk_Nr'].values.astype(int).tolist()
    Stadtteil_Nr3 = ifile3['Stadtteil_Nr'].values.astype(int).tolist()
    Stadtbezirk_Nr3 = ifile3['Stadtbezirk_Nr'].values.astype(int).tolist()
    Postleitzahl3 = ifile3['Postleitzahl'].values.astype(int).tolist()
    Polizeirevier3 = ifile3['Polizeirevier'].values.astype(int).tolist()
    Sozialrathaus_Nr3 = ifile3['Sozialrathaus_Nr'].values.astype(int).tolist()
    
    Ortsbezirk_Nr = np.nan * np.empty(IDLength)
    Stadtteil_Nr = np.nan * np.empty(IDLength)
    Stadtbezirk_Nr = np.nan * np.empty(IDLength)
    Postleitzahl = np.nan * np.empty(IDLength)
    Polizeirevier = np.nan * np.empty(IDLength)
    Sozialrathaus_Nr = np.nan * np.empty(IDLength)
    ############################################################################
    # in this loop, the exact building matches as well as districts are found.
    for i, item0 in enumerate(OBJ):
        goldenIndex = -1
        flag = 1
        flag1 = 0
        flag2 = 0
        flag3 = 1
        high_flag = 0
        if item0 != 'None':
            if i%50000 == 0:
                print(i)
            addresses = item0.split("|")
            if addresses[-1] == "":
                del(addresses[-1])
            for address in addresses:
                address = address.strip()
                temp = address.replace("  "," ")
                temp2 = temp.split(" ")                   
                street = str(int(temp2[0]))
                temp3 = temp2[1:]
                HausNr2 = ''.join(temp3)
                if len(HausNr2)==0:
                    continue
                if flag == 1:
                    newAddress = street + ' ' + HausNr2
                    EqCases = np.argwhere(obj1 == newAddress)
                    temp4 = footprint1[EqCases] == Footprint[i]
                    if True in temp4:
                        temp5 = EqCases[temp4]
                        high_flag = 1
                        for m in range(temp5.size):
                            element = temp5[m]
                            if GINDEX1[element] != -1:
                                FloorNr_Access[i] = FloorNr1[element]
                                GIndex_Access[i] = GINDEX1[element]
                                Footprint_Access[i] = footprint1[element]
                                GArt[i] = GEBAEUDEART1[element]
                                GINDEX1[element] = -1
                                high_flag = 0
                                flag = 0
                                flag1 = 1
                                break
                if flag3 == 1:
                    if "-" in HausNr2:
                        underScoreIndex = HausNr2.index('-')
                        HausNr2 = HausNr2[:underScoreIndex]
                    '''
                    In case the HausNr2 starts with a number, the following split 
                    command returns a '' as the first element of the list. to skip
                    this case, from the first element is considered.
                    in the following, the assumption is that the house number 
                    starts with a number. In case of Frankfurt, it is not 
                    completely true, since there are a few exceptions. However,
                    comparing different tables in Access database, shows that it
                    will not affect the following process.
                    '''
                    number, additional = re.split('(\d+)',HausNr2)[1:]
                    additional = additional.lower()
                    street = int(street)
                    number = int(number)
                    index1 = np.argwhere(strNr==street)
                    l = index1.size
                    for item in index1:
                        # For cases other than Frankfurt (Frankfurt as long as dataset has not
                        # changed), you should also check Nr_to in the next if statement
                        item_elem0 = int(item[0])
                        if np.isnan(Nr_from[item_elem0]):
                            goldenIndex = item_elem0
                            break
                        else:
                            if Nr_from[item_elem0] % 2 == number % 2:
                                if Nr_from[item_elem0] < number and Nr_to[item_elem0] > number:
                                    goldenIndex = item_elem0
                                    break
                                elif Nr_from[item_elem0] == number:
                                    if str(add1[item_elem0]) == 'nan':
                                        goldenIndex = item_elem0
                                        break
                                    else:
                                        if add1[item_elem0].lower() <= additional:
                                            goldenIndex = item_elem0
                                            break
                                elif Nr_to[item_elem0] == number:
                                    if str(add2[item_elem0]) == 'nan':
                                        goldenIndex = item_elem0
                                        break
                                    else:
                                        if add2[item_elem0].lower() >= additional:
                                            goldenIndex = item_elem0
                                            break
                                else:
                                    goldenIndex = -1
                if goldenIndex != -1:
                    flag3 = 0
                    flag2 = 1
                if flag1 == 1 and flag2 == 1:
                    break
            
            if high_flag:
                # this means that str-hNr-FloorArea match exist, but
                # they are already attributed
                high_flag = 0
                GIndex_Access[i] = -1
            if goldenIndex != -1:
                #print(goldenIndex)
                Ortsbezirk_Nr[i] = Ortsbezirk_Nr3[goldenIndex]
                Stadtteil_Nr[i] = Stadtteil_Nr3[goldenIndex]
                Stadtbezirk_Nr[i] = Stadtbezirk_Nr3[goldenIndex]
                Postleitzahl[i] = Postleitzahl3[goldenIndex]
                Polizeirevier[i] = Polizeirevier3[goldenIndex]
                Sozialrathaus_Nr[i] = Sozialrathaus_Nr3[goldenIndex]
    
    
    # This loop is run for finding the matches with threshold concept
    for i, item0 in enumerate(OBJ):
        if np.isnan(GIndex_Access[i]):
            if i%50000 == 0:
                print(i)
            if item0 != 'None': 
                addresses = item0.split("|")
                if addresses[-1] == "":
                    del(addresses[-1])
                q = 0
                flag = 0
                th_flag = 1
                while th_flag:
                    for address in addresses:
                        address = address.strip()
                        temp = address.replace("  "," ")
                        temp2 = temp.split(" ")                   
                        street = str(int(temp2[0]))
                        temp3 = temp2[1:]
                        HausNr2 = ''.join(temp3)
                        if len(HausNr2)==0:
                            continue
                        newAddress = street + ' ' + HausNr2
                        EqCases = np.argwhere(obj1 == newAddress)
                        temp4 = np.absolute(footprint1[EqCases] - Footprint[i]) < areaThresholdList[q]
                        if True in temp4:
                            temp5 = EqCases[temp4]
                            high_flag = 1
                            for m in range(temp5.size):
                                element = temp5[m]
                                if GINDEX1[element] != -1:
                                    FloorNr_Access[i] = FloorNr1[element]
                                    GIndex_Access[i] = GINDEX1[element]
                                    Footprint_Access[i] = footprint1[element]
                                    GArt[i] = GEBAEUDEART1[element]
                                    GINDEX1[element] = -1
                                    flag = 1
                                    high_flag = 0
                                    break
                        if flag:
                            flag = 0
                            th_flag = 0
                            break
                    if high_flag:
                        # this means that str-hNr-FloorArea match does not exist,
                        # With threshold, match is found however, it was
                        # already attributed
                        high_flag = 0
                        GIndex_Access[i] = -2
                    if q < maxIndex_areaThresholdList:
                        q += 1
                    else:
                        th_flag = 0    
    art = np.argwhere(GArt == 99999)
    for item in art:
        keyVal = str(KGF[item[0]])
        if keyVal[-2:] != '.0':
            keyVal = keyVal + '.0'
        GArt[item[0]] = dict_typ_conv[keyVal] 
    orig_spec_dem = demand_typ[GArt].astype(float)
    spec_dem = np.copy(orig_spec_dem)
    residential = np.argwhere((GArt>0) & (GArt<5))
    residential_district =  Stadtbezirk_Nr[residential]
    #residential_district = residential_district[~np.isnan(residential_district)]
    residential_district_index = np.zeros(residential_district.size - 1)
    for i, item in enumerate(residential_district):
        if ~np.isnan(item):
            spec_dem[residential[i]] = specific_demand_res[dict_dist_demand[int(item)],GArt[residential[i]]]
            
    #specific_demand_res[np.argwhere(residential_district)
    
    #Demand = GFA * spec_dem          
    ifile2['Footprint_Access'] = pd.Series(Footprint_Access)            
    ifile2['FloorNr_Access'] = pd.Series(FloorNr_Access)
    ifile2['GIndex_Access'] = pd.Series(GIndex_Access)
    ifile2['GArt'] = pd.Series(GArt)
    ifile2['Orig_Spec_Demand'] = pd.Series(orig_spec_dem)
    ifile2['Spec_Demand'] = pd.Series(spec_dem)
    ifile2['Ortsbezirk_Nr'] = pd.Series(Ortsbezirk_Nr)
    ifile2['Stadtteil_Nr'] = pd.Series(Stadtteil_Nr)
    ifile2['Stadtbezirk_Nr'] = pd.Series(Stadtbezirk_Nr)
    ifile2['Postleitzahl'] = pd.Series(Postleitzahl)
    ifile2['Polizeirevier'] = pd.Series(Polizeirevier)
    ifile2['Sozialrathaus_Nr'] = pd.Series(Sozialrathaus_Nr)
    
    
    
    col = ["ID", "GIndex_Access", "Ortsbezirk_Nr", "Stadtteil_Nr", "Stadtbezirk_Nr", \
           "Postleitzahl", "Polizeirevier", "Sozialrathaus_Nr", "SDG", \
           "GArt", "KGF", "OBJ", "Footprint", "Footprint_Access", "NrFloor", "FloorNr_Access", "GFA", "Orig_Spec_Demand", "Spec_Demand", "X", "Y"]

    ifile2 = ifile2[col]
    ifile2 = ifile2.sort_values(["ID"])
    ifile2.to_csv(outputCSV)
    
    
if __name__ == "__main__":
    start = time.time()
    inputCSV1 = "/home/simulant/ag_lukas/personen/Mostafa/" \
                "Frankfurt Buildingblocks/GEBAEUDE_Access.csv"
    inputCSV2 = "/home/simulant/ag_lukas/personen/Mostafa/" \
                "Frankfurt Buildingblocks/Frankfurt_coords_noDemandEntries.csv"
    inputCSV3 = "/home/simulant/ag_lukas/personen/Mostafa/" \
                "Frankfurt Buildingblocks/Tab_Strvz.csv"
    specificDemand = "/home/simulant/ag_lukas/personen/Mostafa/" \
                "Frankfurt Buildingblocks/Specific_Demand_Residential.csv"
    outputCSV1 = "/home/simulant/ag_lukas/personen/Mostafa/Frankfurt Buildingblocks/Frankfurt_matched_stepwise_th_noDem_sophisticated.csv"
    outputCSV2 = "/home/simulant/ag_lukas/personen/Mostafa/Frankfurt Buildingblocks/Frankfurt_matched_stepwise_th_sophisticated.csv"
    match(inputCSV1, inputCSV2, inputCSV3, specificDemand, outputCSV1)
    inputCSV2 = "/home/simulant/ag_lukas/personen/Mostafa/" \
               "Frankfurt Buildingblocks/Frankfurt_coords.csv"
    match(inputCSV1, inputCSV2, inputCSV3, specificDemand, outputCSV2)
    print(time.time() - start)
    