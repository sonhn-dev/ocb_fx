import numpy as np
import pandas as pd
import re
import os

def load_files(dir):
    """ Load txt files to dataframe """

    data = []
    for filename in os.listdir(dir):
        filepath = os.path.sep.join([dir, filename])
        try:
            date = re.findall(r'^(\d\d\d\d\d\d\d\d)\.txt$', filename)[0]
            with open(filepath, encoding='utf-8') as file:
                for line in file.read().splitlines():
                    data.append((date, line))
        except:
            pass
  
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
    pat = '(.*)\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov)\s\d+\s(.*)$'
    r = re.compile(pat)
    df[['trader', 'bank']] = df['text'].str.extract(r)
    cond = df[['time', 'trader', 'bank']].isna().all(axis='columns')
    df.fillna(method='ffill', axis='rows', inplace=True)
    df = df[cond]
    df = df[~df['time'].isna()]

    df['group'] = 0
    cols = df.columns.to_list()
    trader_idx = cols.index('trader')
    date_idx = cols.index('date')
    group_idx = cols.index('group')
    for i in range(1, df.shape[0]):
        if (df.iloc[i, date_idx] == df.iloc[i-1, date_idx] and
            df.iloc[i, trader_idx] == df.iloc[i-1, trader_idx]):
            df.iloc[i, group_idx] = df.iloc[i-1, group_idx]
        else:
            df.iloc[i, group_idx] = df.iloc[i-1, group_idx] + 1

    df = df.groupby(['date', 'group'], as_index=False).agg({
        'trader': 'first',
        'bank': 'first',
        'time': np.max,
        'text': lambda s: '. '.join(s)
    })
    df.drop('group', axis='columns', inplace=True)
    return df
