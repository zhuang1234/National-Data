import pandas as pd
import numpy as np
import os
import json
import time

quarter = dict(第一季度="A", 第二季度="B", 第三季度="C", 第四季度="D")


def date_ym(date):
    return time.strftime("%Y-%m", time.strptime(date, "%Y年%m月"))


def date_qm(date):
    q = date.split("年")[1]
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


def month_process(df):
    if len(df.index.values) and "月" in df.index.values[0]:
        df.index = list(map(date_ym, df.index.values))
    df = df.sort_index(ascending=True)
    for value in df.columns.values:
        if "累计值" in value:
            name = value.split("_累计值")[0]
            df[name] = df[value].rolling(2, min_periods=1).apply(org_data)


def quarter_process(df):
    if len(df.index.values) and "度" in df.index.values[0]:
        df.index = list(map(date_qm, df.index.values))
    df = df.sort_index(ascending=True)
    # print(df)
    for value in df.columns.values:
        if "累计值" in value:
            name = value.split("_累计值")[0]
            df[name] = df[value].rolling(2, min_periods=1).apply(org_data)


def check_dir(name_list):
    # if type(name_list) in [str,unicode]:
    if type(name_list) in [str, bytes]:
        name_list = name_list.replace("\\", "/").split("/")
    now_path = name_list[0]
    for name in name_list[1:]:
        if not os.path.isdir(now_path):
            os.mkdir(now_path)
        now_path = os.path.join(now_path, name)


class Document(object):
    def __init__(self, raw_root="raw"):
        self.raw_root = raw_root

    def get(self, name):
        path = os.path.join(self.raw_root, name)
        print(path)
        with open(path, "r", encoding="utf8") as f:
            line = f.readline().strip("\n")
            if line == "<!DOCTYPE html>":
                return False
        with open(path, "r", encoding="utf8") as f:
            content = f.read()
        return content

    def get_json(self, name):
        res = self.get(name)
        if res is False:
            return res
        return json.loads(res)

    def json_to_dataframe(self, dic, origin_code=True):
        # assert dic['returncode'] == 200
        if dic["returncode"] != 200:
            return False
        returndata = dic["returndata"]
        datanodes, wdnodes = returndata["datanodes"], returndata["wdnodes"]
        if not origin_code:  # parse wdnodes for transform that
            wd = {w["wdcode"]: {ww["code"]: ww["cname"] for ww in w["nodes"]} for w in wdnodes}  # noqa: E501
            zb_wd, sj_wd = wd["zb"], wd["sj"]
        rd = {}
        for node in datanodes:
            sd = {w["wdcode"]: w["valuecode"] for w in node["wds"]}
            zb, sj = sd["zb"], sd["sj"]
            if not origin_code:
                zb, sj = zb_wd[zb], sj_wd[sj]
            rd[(sj, zb)] = node["data"]["data"] if node["data"]["hasdata"] else np.NaN
        df = pd.Series(rd).unstack()
        return df

    def get_dataframe(self, name, origin_code=False):
        res = self.get_json(name)
        if res is False:
            return res
        return self.json_to_dataframe(res, origin_code=False)

    def to_excel(self, name, path, file_type):
        # print(name, path)
        df = self.get_dataframe(name)
        if df is False:
            print(f"Error:{name} download fail! {path} not generated!!")
            return
        if file_type in ["M", "m", "month", "Month"]:
            month_process(df)
        elif file_type in ["Q", "q", "quarter", "Quarter"]:
            quarter_process(df)
        df.dropna(how="all", inplace=True)
        df.to_excel(path)

    def iter_tree(self, tree, path=("zb",), origin_dir=False):
        yield path, tree
        for node in tree.children:
            newpath = path + ((node.id,) if origin_dir else (node.name,))
            for r in self.iter_tree(node, path=newpath):
                yield r

    def to_excel_all(self, tree, root="data", file_type=None):
        for path, node in self.iter_tree(tree):
            if node.leaf and os.path.exists(os.path.join(self.raw_root, node.id)):
                path = list(path)
                if "/" in path[-1]:
                    path[-1] = path[-1].replace("/", "_")
                path_t = [
                    root,
                ] + path
                check_dir(path_t)
                self.to_excel(node.id, os.path.join(*path_t) + ".xlsx", file_type)
