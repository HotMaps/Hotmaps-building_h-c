import time
import re
import pandas as pd
import numpy as np


def match_floors(inputCSV1, inputCSV2, outputCSV):
    # Building demand based on type [GWh/m2/a]
    # Frankfurt has no data regarding age of the building. In case such data exist
    # it should be considered in calculation.
    # demand types: 0: no demand; 1: einzelhaus; 2: Doppelhaus, 3: Reihenhaus; 4: Mehrfamilienhaus; 5:Mischnutzung; 6: Buero
    # 7: Gewerbe; 8 Beherbergung; 9: Gastronomie; 10:oeffentliches Gebaeude; 11: Schule; 12: Krankenhaus; 13: Schwimmbad
    demand_typ = np.array([0, 219, 212, 205, 134, 189, 177, 220, 269, 253, 144, 157, 311, 311]) * 0.000001
    # Building types based on the category provided in the shapefile. This 
    # category is used for those entries that do not exist in the Access database.
    dict_typ_conv = {
             "1000.0":1,"1020.0":4,"1022.0":4,"1100.0":3,"1120.0":3,"1223.0":4,
             "2010.0":3,"2020.0":3,"2030.0":5,"2040.0":3,"2051.0":3,"2052.0":3,
             "2053.0":3,"2055.0":3,"2056.0":3,"2060.0":5,"2070.0":4,"2071.0":4,
             "2074.0":4,"2081.0":4,"2090.0":5,"2092.0":5,"2100.0":3,"2130.0":0,
             "2320.0":3,"2410.0":3,"2420.0":3,"2430.0":3,"2431.0":3,"2443.0":3,
             "2460.0":0,"2461.0":0,"2462.0":0,"2463.0":0,"2465.0":0,"2501.0":0,
             "2510.0":3,"2511.0":3,"2513.0":0,"2520.0":0,"2522.0":0,"2523.0":0,
             "2540.0":3,"2570.0":0,"2580.0":3,"2620.0":0,"2700.0":3,"2721.0":0,
             "2723.0":0,"2740.0":3,"3010.0":3,"3012.0":5,"3013.0":5,"3014.0":5,
             "3015.0":5,"3016.0":5,"3020.0":5,"3021.0":5,"3022.0":5,"3023.0":5,
             "3024.0":5,"3030.0":5,"3031.0":5,"3032.0":5,"3033.0":5,"3034.0":5,
             "3035.0":3,"3036.0":5,"3037.0":5,"3040.0":5,"3041.0":5,"3042.0":5,
             "3044.0":5,"3045.0":5,"3046.0":5,"3047.0":5,"3048.0":5,"3050.0":6,
             "3051.0":6,"3052.0":6,"3060.0":5,"3061.0":4,"3062.0":4,"3065.0":5,
             "3070.0":5,"3071.0":3,"3072.0":3,"3073.0":4,"3074.0":0,"3075.0":4,
             "3080.0":0,"3081.0":5,"3082.0":0,"3091.0":5,"3092.0":5,"3094.0":5,
             "3095.0":5,"3097.0":3,"3211.0":5,"3221.0":7,"3222.0":7,"3230.0":3,
             "3260.0":3,"3270.0":3,"3290.0":5,"11491.0":4,"13074.0":0,"19950.0":0,
             "19951.0":0,"19952.0":0,"19953.0":5
            }
    ############################################################################
    # Access building blocks
    ifile1 = pd.read_csv(inputCSV1).astype('str')
    ifile1 = ifile1.sort_values(["STRASSENKENNZIFFER","HAUSNUMMER"])
    Strvrz1 = ifile1['STRASSENKENNZIFFER'].values
    HausNr1 = ifile1['HAUSNUMMER'].values.tolist()
    floorArea1 = ifile1['FLAECHE'].values.astype(float)
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
    NFA = ifile2['NFA'].values.astype(float).tolist()
    OBJ = ifile2['OBJ'].values.astype(str).tolist()
    KGF = ifile2['KGF'].values.astype(int)
    GFA = ifile2['GFA'].values.astype(float)
    IDLength = len(ID)
    FloorNr_Access = np.nan * np.empty(IDLength)
    GIndex_Access = np.nan * np.empty(IDLength)
    FloorArea_Access = np.nan * np.empty(IDLength)
    GArt = np.zeros(IDLength).astype(int)
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
    
    goldenIndex = -1
    # threshold for the area difference [m2]
    areathreshold = 2
    
    for i, item in enumerate(OBJ):
        flag = 1
        flag1 = 0
        flag2 = 0
        flag3 = 1
        if item != 'None':
            print(i)
            addresses = item.split("|")
            if addresses[-1] == "":
                del(addresses[-1])
            for address in addresses:
                address = address.strip()
                temp = address.replace("  "," ")
                temp2 = temp.split(" ")                   
                street = str(int(temp2[0]))
                temp3 = temp2[1:]
                HausNr2 = ''.join(temp3)
                if flag == 1:
                    newAddress = street + ' ' + HausNr2
                    EqCases = np.argwhere(obj1 == newAddress)
                    temp4 = floorArea1[EqCases] == NFA[i]
                    if True in temp4:
                        temp5 = EqCases[temp4]
                        FloorNr_Access[i] = FloorNr1[temp5][0]
                        GIndex_Access[i] = GINDEX1[temp5][0]
                        FloorArea_Access[i] = floorArea1[temp5][0]
                        GArt[i] = GEBAEUDEART1[temp5][0]
                        flag = 0
                        flag1 = 1
                    else:
                        temp4 = np.absolute(floorArea1[EqCases] - NFA[i]) < areathreshold
                        if True in temp4:
                            temp5 = EqCases[temp4]
                            FloorNr_Access[i] = FloorNr1[temp5][0]
                            GIndex_Access[i] = GINDEX1[temp5][0]
                            FloorArea_Access[i] = floorArea1[temp5][0]
                            GArt[i] = GEBAEUDEART1[temp5][0]
                            flag = 0
                            flag1 = 1
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
                        if np.isnan(Nr_from[int(item[0])]):
                            goldenIndex = int(item[0])
                            break
                        else:
                            if Nr_from[int(item[0])] < number and Nr_to[int(item[0])] > number:
                                goldenIndex = int(item[0])
                                break
                            elif Nr_from[int(item[0])] == number:
                                if str(add1[int(item[0])]) == 'nan':
                                    goldenIndex = int(item[0])
                                    break
                                else:
                                    if add1[int(item[0])].lower() <= additional:
                                        goldenIndex = int(item[0])
                                        break
                            elif Nr_to[int(item[0])] == number:
                                if str(add2[int(item[0])]) == 'nan':
                                    goldenIndex = int(item[0])
                                    break
                                else:
                                    if add2[int(item[0])].lower() >= additional:
                                        goldenIndex = int(item[0])
                                        break
                            else:
                                goldenIndex = -1
                if goldenIndex != -1:
                    flag3 = 0
                    flag2 = 1
                if flag1 == 1 and flag2 == 1:
                    break
            if goldenIndex != -1:
                #print(goldenIndex)
                Ortsbezirk_Nr[i] = Ortsbezirk_Nr3[goldenIndex]
                Stadtteil_Nr[i] = Stadtteil_Nr3[goldenIndex]
                Stadtbezirk_Nr[i] = Stadtbezirk_Nr3[goldenIndex]
                Postleitzahl[i] = Postleitzahl3[goldenIndex]
                Polizeirevier[i] = Polizeirevier3[goldenIndex]
                Sozialrathaus_Nr[i] = Sozialrathaus_Nr3[goldenIndex]
    art = np.argwhere(GArt>14)
    for item in art:
        GArt[item[0]] = dict_typ_conv[KGF[item[0]]]  
    Demand = GFA * demand_typ[GArt]          
    ifile2['NFA_Access'] = pd.Series(FloorArea_Access)            
    ifile2['FloorNr_Access'] = pd.Series(FloorNr_Access)
    ifile2['GIndex_Access'] = pd.Series(GIndex_Access)
    ifile2['GArt'] = pd.Series(GArt)
    ifile2['Demand'] = pd.Series(Demand)
    ifile2['Ortsbezirk_Nr'] = pd.Series(Ortsbezirk_Nr)
    ifile2['Stadtteil_Nr'] = pd.Series(Stadtteil_Nr)
    ifile2['Stadtbezirk_Nr'] = pd.Series(Stadtbezirk_Nr)
    ifile2['Postleitzahl'] = pd.Series(Postleitzahl)
    ifile2['Polizeirevier'] = pd.Series(Polizeirevier)
    ifile2['Sozialrathaus_Nr'] = pd.Series(Sozialrathaus_Nr)
    
    
    
    col = ["ID", "GIndex_Access", "Ortsbezirk_Nr", "Stadtteil_Nr", "Stadtbezirk_Nr", \
           "Postleitzahl", "Polizeirevier", "Sozialrathaus_Nr", "SDG", \
           "GArt", "KGF", "OBJ", "NFA", "NFA_Access", "NrFloor", "FloorNr_Access", "GFA", "Demand", "X", "Y"]

    ifile2 = ifile2[col]
    ifile2 = ifile2.sort_values(["ID"])
    ifile2.to_csv(outputCSV)
    
    
if __name__ == "__main__":
    start = time.time()
    inputCSV1 = "/home/simulant/ag_lukas/personen/Mostafa/" \
                "Frankfurt Buildingblocks/GEBAEUDE_Access.csv"
    inputCSV2 = "/home/simulant/ag_lukas/personen/Mostafa/" \
                "Frankfurt Buildingblocks/Frankfurt_coords.csv"
    inputCSV3 = "/home/simulant/ag_lukas/personen/Mostafa/" \
                "Frankfurt Buildingblocks/Tab_Strvz.csv"
    outputCSV = "/home/simulant/ag_lukas/personen/Mostafa/Frankfurt Buildingblocks/Frankfurt_Data_matched.csv"
    match_floors(inputCSV1, inputCSV2, outputCSV)
    print(time.time() - start)