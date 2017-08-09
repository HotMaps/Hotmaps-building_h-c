import pandas as pd
import time
# test

def csvedit(inputCSV,outputCSV):
    ifile = pd.read_csv(inputCSV).astype('str')
    ID = ifile['ID'].values.astype(int).tolist()
    SDG = ifile['SDG'].values.tolist()
    KGF = ifile['KGF'].values.tolist()
    OBJ = ifile['OBJ'].values.tolist()
    NFA = ifile['NFA'].values.tolist()
    NrFloor = ifile['NrFloor'].values.tolist()
    GFA = ifile['GFA'].values.tolist()
    X = ifile['X'].values.tolist()
    Y = ifile['Y'].values.tolist()
    nRows = len(ID)
    delList = []
    for i in range(nRows):
        temp = OBJ[i].split("|")
        k = len(temp)
        if temp[k-1]=="":
            del(temp[k-1])
            k = k - 1
        if k > 1:
            delList.append(i)
            for j in range(k):
                ID.append(ID[i])
                OBJ.append(temp[j])
                KGF.append(KGF[i])
                SDG.append(SDG[i])
                NFA.append(NFA[i])
                NrFloor.append(NrFloor[i])
                GFA.append(GFA[i])
                X.append(X[i])
                Y.append(Y[i])
    
    d = {"ID": ID, "NrFloor": NrFloor, "NFA": NFA, "GFA": GFA, "KGF": KGF, "SDG": SDG, "OBJ": OBJ, "X": X, "Y": Y}
    df = pd.DataFrame(d)
    df = df.drop(df.index[delList])
    df = df.sort_values(["ID","OBJ"])
    #df = df.sort(["ID","OBJ"])
    
   
    ID = df['ID'].values.astype(int).tolist()
    OBJ = df['OBJ'].values.tolist() 
    KGF = df['KGF'].values.tolist()
    SDG = df['SDG'].values.tolist()
    NFA = df['NFA'].values.tolist()
    NrFloor = df['NrFloor'].values.tolist()
    GFA = df['GFA'].values.tolist()
    X = df['X'].values.tolist()
    Y = df['Y'].values.tolist()
    df = d =None
    Strvrz = []
    HausNr = []
    proof = [] # the aim of this list is to show those rows that only contain Strvz
    nRows = len(ID)
    for i in range(nRows):
        proof.append(-1)
        OBJ[i] = OBJ[i].replace("  ", " ")
        temp = OBJ[i].split(" ")
        k = len(temp)
        if temp[k-1]=="":
            del(temp[k-1])
            k = k - 1
        if temp[k-1]=="":
            del(temp[k-1])
            k = k - 1
        if k > 2:
            #print(temp)
            temp = [temp[0],temp[1]+temp[2]+temp[3]] # e.g. 5 - 7 --> 5-7
            k = len(temp)
        if temp[0] == "None":
                temp[0] = -1
        if k > 1:
            Strvrz.append(int(temp[0]))
            HausNr.append(temp[1])
            proof[i] = 1

        else:
            Strvrz.append(int(temp[0]))
            HausNr.append(-1)
            proof[i] = 0
    if len(proof) != len(OBJ):
        raise()
        
    d = {"ID": ID, "Proof": proof, "NFA": NFA, "NrFloor": NrFloor, "GFA": GFA, "KGF": KGF, "SDG": SDG, "OBJ": OBJ, "Strvrz": Strvrz, "HausNr": HausNr, "X": X, "Y": Y}
    col = ["ID", "Proof", "SDG", "KGF", "OBJ", "Strvrz", "HausNr", "NFA", "NrFloor", "GFA", "X", "Y"]
    df = pd.DataFrame(d)
    df = df[col]
    df = df.sort_values(["ID","Strvrz", "HausNr"])
    #df = df.sort(["ID","Strvrz", "HausNr"])
    #df = df.drop('ID', axis = 1)
    df.to_csv(outputCSV)

    
if __name__ == "__main__":
    start = time.time()
    inputCSV = "/home/simulant/ag_lukas/personen/Mostafa/Frankfurt Buildingblocks/Frankfurt_coords.csv"
    outputCSV = "/home/simulant/ag_lukas/personen/Mostafa/Frankfurt Buildingblocks/Frankfurt_Data.csv"
    csvedit(inputCSV,outputCSV)
    print(time.time() - start)