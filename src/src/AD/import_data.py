'''
Created on 08.05.2017

@author: fritz
'''

import os
import csv
import json

import numpy as np
import pandas as pandas
from pandas import HDFStore,DataFrame



def read_data_set_csv( filename ):
    data = []
    data = pandas.read_csv(filename, encoding = "ISO-8859-1")
    return data

###not final
def read_data_set_csv_NUTS0( filename, idx_Nuts0 ):
    data = []
    data = pandas.read_csv(filename, encoding = "ISO-8859-1")
    return data

def read_data_set_csv_NUTS3( filename , idx_NUTS3):
    data = []
    data = pandas.read_csv(filename, encoding = "ISO-8859-1")
    match_index_nuts3 = data.idx_NUTS3[data.idx_NUTS3==idx_NUTS3].index
    data = data.loc[match_index_nuts3,:]
    return data
