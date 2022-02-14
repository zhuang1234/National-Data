import os
import pandas as pd
from time import strftime, strptime

quarter = dict(第一季度='A', 第二季度='B', 第三季度='C', 第四季度='D')


def date_ym(date):
    date1 = strptime(date, '%Y年%m月')
    date = strftime('%Y-%m', date1)
    return date


def date_qm(date):
    q = date.split('年')[1]
    return date.replace(q, quarter[q])


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
def month_process():
    for root, Dirs, files in os.walk('.\\data_month'):
        for file in files:
            if '.xlsx' in file:
                path = os.path.join(root, file)
                df = pd.read_excel(path, index_col=0)
                # print(date_ym('2019年9月'))
                print(path)
                if len(df.index.values) and '月' in df.index.values[0]:
                    df.index = list(map(date_qm, df.index.values))
                df = df.sort_index(ascending=True)
                for value in df.columns.values:
                    if '累计值' in value:
                        name = value.split('_累计值')[0]
                        df[name] = df[value].rolling(2, min_periods=1).apply(org_data)
                # df = df.sort_index(ascending=True)
                # print(df)
                df.to_excel(path)
                # exit()


def quarter_process():
    for root, Dirs, files in os.walk('.\\data_quarter'):
        for file in files:
            if '.xlsx' in file:
                path = os.path.join(root, file)
                print(path)
                df = pd.read_excel(path, index_col=0)
                if len(df.index.values) and '度' in df.index.values[0]:
                    df.index = list(map(date_qm, df.index.values))
                df = df.sort_index(ascending=True)
                # print(df)
                for value in df.columns.values:
                    if '累计值' in value:
                        name = value.split('_累计值')[0]
                        df[name] = df[value].rolling(2, min_periods=1).apply(org_data)
                # df = df.sort_index(ascending=True)
                # print(df)
                df.to_excel(path)
                # exit()


if __name__ == '__main__':
    # month_process()
    quarter_process()
