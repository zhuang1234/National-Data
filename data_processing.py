import os
import pandas as pd
from time import strftime, strptime


def date_ym(date):
    date1 = strptime(date, '%Y年%m月')
    date = strftime('%Y-%m', date1)
    return date


def org_data(data):
    values = data.values
    if len(values) > 1:
        if values[1] > values[0]:
            return values[1] - values[0]
        else:
            return values[1]
    else:
        return values[0]


# for root, Dir, file in os.walk(os.path.dirname(os.path.abspath(__file__))):
for root, Dirs, files in os.walk('.\\data_month'):
    for file in files:
        if '.xlsx' in file:
            path = os.path.join(root, file)
            df = pd.read_excel(path, index_col=0)
            # print(date_ym('2019年9月'))
            if '月' in df.index.values:
                df.index = list(map(date_ym, df.index.values))
            for value in df.columns.values:
                if '累计值' in value:
                    name = value.split('_累计值')[0]
                    df[name] = df[value].rolling(2, min_periods=1).apply(org_data)
            # df = df.sort_index(ascending=True)
            # print(df)
            df.to_excel(path)
            # exit()
