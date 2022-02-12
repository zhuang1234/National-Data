import os
import pandas as pd
from time import strftime, strptime


def date_ym(date):
    date1 = strptime(date, '%Y年%m月')
    date = strftime('%Y-%m', date1)
    return date


def org_data(value1):
    print(value1)



# for root, Dir, file in os.walk(os.path.dirname(os.path.abspath(__file__))):
for root, Dirs, files in os.walk('.\\data_month'):
    for file in files:
        if '.xlsx' in file:
            with open(os.path.join(root, file), 'rb') as f:
                df = pd.read_excel(f, index_col=0)
                # print(date_ym('2019年9月'))
                df.index = list(map(date_ym, df.index.values))
                df = df.sort_index()
                # print
                for value in df.columns.values:
                    if '累计值' in value:
                        name = value.split('_累计值')[0]
                        print(df[value].rolling(2))
                        df[name] = df[value].rolling(2).apply(org_data)
                print(df.columns.values)
                # df = df.apply(lambda x: date_ym(x))
                # print(df)
                exit()
