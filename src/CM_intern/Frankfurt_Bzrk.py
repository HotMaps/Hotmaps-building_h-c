import re
import pandas as pd
import numpy as np
import time




def add_bzrk(inputCSV1, inputCSV2, outputCSV):
    ifile1 = pd.read_csv(inputCSV1)
    csv1values = ifile1.values
    col1 = ifile1.columns.values
    nRow1 = csv1values.shape[0]
    strNr = ifile1['strNr'].values.astype(int)
    Nr_from = ifile1['Nr_from'].tolist()
    add1 = ifile1['add1'].values.tolist()
    Nr_to = ifile1['Nr_to'].values.tolist()
    add2 = ifile1['add2'].values.tolist()
    Ortsbezirk_Nr1 = ifile1['Ortsbezirk_Nr'].values.astype(int).tolist()
    Stadtteil_Nr1 = ifile1['Stadtteil_Nr'].values.astype(int).tolist()
    Stadtbezirk_Nr1 = ifile1['Stadtbezirk_Nr'].values.astype(int).tolist()
    Postleitzahl1 = ifile1['Postleitzahl'].values.astype(int).tolist()
    Polizeirevier1 = ifile1['Polizeirevier'].values.astype(int).tolist()
    Sozialrathaus_Nr1 = ifile1['Sozialrathaus_Nr'].values.astype(int).tolist()
    
    ifile2 = pd.read_csv(inputCSV2)
    ID = ifile2['ID'].values.tolist()
    SDG = ifile2['SDG'].values.tolist()
    GArt = ifile2['GArt'].values.tolist()
    KGF = ifile2['KGF'].values.tolist()
    OBJ = ifile2['OBJ'].values.tolist()
    NFA = ifile2['NFA'].values.tolist()
    NrFloor = ifile2['NrFloor'].values.tolist()
    GFA = ifile2['GFA'].values.tolist()
    Demand = ifile2['Demand'].values.tolist()
    X = ifile2['X'].values.tolist()
    Y = ifile2['Y'].values.tolist()
    
    nRow2 = len(ID)
    
    Ortsbezirk_Nr2 = np.nan * np.empty(nRow2)
    Stadtteil_Nr2 = np.nan * np.empty(nRow2)
    Stadtbezirk_Nr2 = np.nan * np.empty(nRow2)
    Postleitzahl2 = np.nan * np.empty(nRow2)
    Polizeirevier2 = np.nan * np.empty(nRow2)
    Sozialrathaus_Nr2 = np.nan * np.empty(nRow2)

    goldenIndex = -1
    for i in range(nRow2):
        if OBJ[i] != 'None':
            temp = OBJ[i].split("|")
            k = len(temp)
            if temp[k-1]=="":
                del(temp[k-1])
                k = k - 1
            for t in range(k):
                temp1 = temp[t]
                if temp1[-1] == " ":
                    temp1 = temp1[:-1]
                temp1 = temp1.replace("  "," ")
                temp2 = temp1.split(" ")
                if len(temp2) < 2:
                    continue
                if len(temp2) > 2:
                    print('warning temp2')
                    continue
                s = temp2[0]
                n = temp2[1]
                if "-" in n:
                    underScoreIndex = n.index('-')
                    n = n[:underScoreIndex]
                number, additional = re.split('(\d+)',n)[1:]
                additional = additional.lower()
                s = int(s)
                number = int(number)
                index1 = np.argwhere(strNr==s)
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
                    break
            #if s == 613:    
            if goldenIndex != -1:
                #print(goldenIndex)
                Ortsbezirk_Nr2[i] = Ortsbezirk_Nr1[goldenIndex]
                Stadtteil_Nr2[i] = Stadtteil_Nr1[goldenIndex]
                Stadtbezirk_Nr2[i] = Stadtbezirk_Nr1[goldenIndex]
                Postleitzahl2[i] = Postleitzahl1[goldenIndex]
                Polizeirevier2[i] = Polizeirevier1[goldenIndex]
                Sozialrathaus_Nr2[i] = Sozialrathaus_Nr1[goldenIndex]
    Ortsbezirk_Nr = Ortsbezirk_Nr2.tolist()
    Stadtteil_Nr = Stadtteil_Nr2.tolist()
    Stadtbezirk_Nr = Stadtbezirk_Nr2.tolist()
    Postleitzahl = Postleitzahl2.tolist()
    Polizeirevier = Polizeirevier2.tolist()
    Sozialrathaus_Nr = Sozialrathaus_Nr2.tolist()
    d = {"ID": ID, "NFA": NFA, "NrFloor": NrFloor, "GFA": GFA, "KGF": KGF,
         "GArt": GArt, "SDG": SDG, "OBJ": OBJ, "Demand": Demand, "X": X,
         "Y": Y, "Ortsbezirk_Nr": Ortsbezirk_Nr, "Stadtteil_Nr": Stadtteil_Nr,
          "Stadtbezirk_Nr": Stadtbezirk_Nr, "Postleitzahl": Postleitzahl,
          "Polizeirevier": Polizeirevier, "Sozialrathaus_Nr": Sozialrathaus_Nr}
    df = pd.DataFrame(d)
    col = ["ID", "Ortsbezirk_Nr", "Stadtteil_Nr", "Stadtbezirk_Nr", \
           "Postleitzahl", "Polizeirevier", "Sozialrathaus_Nr", "SDG", \
           "GArt", "KGF", "OBJ", "NFA", "NrFloor", "GFA", "Demand", "X", "Y"]
    df = df[col]
    df = df.sort_values(["ID"])
    df.to_csv(outputCSV)
if __name__ == "__main__":
    start = time.time()
    inputCSV1 = "/home/simulant/ag_lukas/personen/Mostafa/" \
                "Frankfurt Buildingblocks/Tab_Strvz.csv"
    inputCSV2 = "/home/simulant/ag_lukas/personen/Mostafa/" \
                "Frankfurt Buildingblocks/Frankfurt_Data_final.csv"
    outputCSV = "/home/simulant/ag_lukas/personen/Mostafa/" \
                "Frankfurt Buildingblocks/Frankfurt_Data_final_complete.csv"
    add_bzrk(inputCSV1, inputCSV2, outputCSV)
    print(time.time() - start)
    