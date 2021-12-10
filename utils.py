import numpy as np
import pandas as pd
import re
import os

def load_files(folder):
    """ Load txt files to dataframe """

    data = []
    i = 0
    for filename in os.listdir(folder):
        filepath = os.path.join(folder, filename)
        try:
            date = re.findall(r'^(\d\d\d\d\d\d\d\d)\.txt$', filename)[0]
            with open(filepath, encoding='utf-8') as file:
                i += 1
                for line in file.read().splitlines():
                    data.append((date, line))
        except:
            pass
    print(i, ' file(s) read')

    df = pd.DataFrame(data)
    df.columns = ['date', 'text']
    df['date'] = pd.to_datetime(df['date'])
    df.reset_index(inplace=True)
    df.sort_values(['date', 'index'], axis='rows', inplace=True)
    df.drop('index', axis='columns', inplace=True)
    return df

def to_structured_data(df):
    """ Convert data to structured data """

    r = re.compile(r'^(\d\d:\d\d:\d\d)$')
    df['time'] = df['text'].str.extract(r)
    pat = r'(.*)\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s\d+\s(.*)$'
    r = re.compile(pat)
    df[['trader', 'bank']] = df['text'].str.extract(r)
    cond = df[['time', 'trader', 'bank']].isna().all(axis='columns')
    df.fillna(method='ffill', axis='rows', inplace=True)
    df = df[cond]
    df = df[~df['time'].isna()]
    df.reindex(drop=True, inplace=True)
 
    return df
