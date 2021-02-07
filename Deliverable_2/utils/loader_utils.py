import json
import numpy as np
import pandas as pd
import calendar
import re

def read_jl_file(file_path):
    '''
    Reads .jl file
    
    Parameter
    ---------
    file_path: str
        path to file
    
    Returns
    -------
    values: list
        list of values stored in original .jl file

    '''
    values = []

    with open(file_path, 'rb') as f:
        line = '---'
        while len(line)>1:
            line = f.readline()
            values.append(line)

    values = values[:-1]
    values = [json.loads(i) for i in values]

    return values

def extract_details(df):
    '''
    Processes the 'resto_keys' and 'resto_details' columns of 
    data frame containing restaurant information

    Parameter
    ---------
    df: pandas.DataFrame
        data frame with restaurant data
    
    Returns
    -------
    df: pandas.DataFrame
        df with 'resto_keys' and 'resto_details' processed

    '''
    col_details = ['Meals', 'PRICE RANGE', 'CUISINES', 
                   'Special Diets', 'FEATURES']
    for col in col_details:
        df.loc[:, col] = np.nan

    df.reset_index(drop=True, inplace=True)
    for idx in df.index:
        keys = df.iloc[idx, :]['resto_keys']
        values = df.iloc[idx, :]['resto_details']
        for k, v in zip(keys, values):
            df.loc[:, k][idx] = v
            
    df.columns = [col.lower() for col in df.columns]

    return df.drop(columns=['resto_keys', 'resto_details'])

def get_resto_id(df, url_type):
    '''
    Extracts the research id and the restaurant id from TA url.

    Parameters
    ----------
    df: pandas.DataFrame
        dataframe to be processed
    url_type: str
        indicates if the df contains restaurant or review information.
        Must be either 'review' or 'resto'
    
    Returns
    -------
    df: pandas.DataFrame
        processed df

    '''
    if url_type == 'review':
        column_name = 'review_url'
    elif url_type =='resto':
        column_name = 'resto_url'
    else:
        raise TypeError('url_type must be either "review" or "resto"')
    
    df['research_id'] = df[column_name].apply(
        lambda x: re.findall(r'\-g(\d+)\-', x)[0]
    )
    df['resto_id'] = df[column_name].apply(
        lambda x: re.findall(r'\-d(\d+)\-', x)[0]
    )

    return df 

def convert_date(df):
    '''Converts 'review_date' column to pd.DateTime objects.'''
    months = {month: str(i) for i, month in enumerate(calendar.month_name)}
    del months[''] # delete month 0
    # extract month
    df['review_month'] = df['review_date'].apply(
        lambda x: x.strip().split(' ')[0] if x is not None else x
    )
    # format month
    df['review_month'] = df['review_month'].replace(months)
    #extract year
    df['review_year'] = df['review_date'].apply(
        lambda x: x.strip().split(' ')[1] if x is not None else x
    )
    # convert to datetime object
    df['review_date'] = df['review_month'] + '-01-' + df['review_year']
    df['review_date'] = pd.to_datetime(df['review_date'])
    # remove columns used for calculation
    df.drop(columns=['review_year', 'review_month'], inplace=True)

    return df