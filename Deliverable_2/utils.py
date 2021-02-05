import json
import numpy as np
import pandas as pd

def read_jl_file(file_name):
    '''
    # TODO
    '''
    values = []

    with open(file_name, 'rb') as f:
        line = '---'
        while len(line)>1:
            line = f.readline()
            values.append(line)

    values = values[:-1]
    values = [json.loads(i) for i in values]

    return values

def extract_details(df):
    '''
    # TODO
    '''
    col_details = ['Meals', 'PRICE RANGE', 'CUISINES', 'Special Diets', 'FEATURES']
    for col in col_details:
        df.loc[:, col] = np.nan

    df.reset_index(drop=True, inplace=True)
    for idx in df.index:
        keys = df.iloc[idx, :]['resto_keys']
        values = df.iloc[idx, :]['resto_details']
        for k, v in zip(keys, values):
            df.loc[:, k][idx] = v
            
    df.columns = [col.lower() for col in df.columns]

    return df