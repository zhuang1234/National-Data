# -*- coding: utf-8 -*-
"""
@author: nashanren
"""
import argparse
import os
import pickle
import sys

import requests
from directory_handler import TreeNode
from document_handler import Document
from download_handler import Downloader
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

url = "http://data.stats.gov.cn/easyquery.htm"


# s = '''id:zb
# dbcode:hgyd
# wdcode:zb
# m:getTree'''
# dic = dict(term.split(':') for term in s.split('\n'))
# res = requests.get(url, params=dic, verify=False)


def parse_event_type(type):
    if args.type in ["Y", "y", "year", "Year"]:
        db_code = "hgnd"
        tree_file = "tree_year"
        raw_file = "raw_year"
    elif args.type in ["M", "m", "month", "Month"]:
        db_code = "hgyd"
        tree_file = "tree_month"
        raw_file = "raw_month"
    elif args.type in ["Q", "q", "quarter", "Quarter"]:
        db_code = "hgjd"
        tree_file = "tree_quarter"
        raw_file = "raw_quarter"
    else:
        print("请输入抓取数据类型，目前暂只支持year、quarter、month")
        exit(1)

    if not os.path.isdir(raw_file):
        os.mkdir(raw_file)
    return db_code, tree_file, raw_file


def init_directory_tree(db_code, tree_file):
    if os.path.isfile(tree_file):
        print("init tree by cache")
        with open(tree_file, "rb") as f:
            tree = pickle.load(f)
    else:
        print("init tree by web")
        tree = TreeNode(dbcode=db_code, url=url)
        tree.get_recur()
        with open(tree_file, "wb") as f:
            print("cache tree information...")
            pickle.dump(tree, f)
    return tree


def run(args):
    db_code, tree_file, raw_file = parse_event_type(args.type)
    tree = init_directory_tree(db_code, tree_file)
    if not os.path.isdir(args.dest):
        os.mkdir(args.dest)

    print("start download file")
    downloader = Downloader(tree, raw_root=raw_file, dbcode=db_code, date=args.date)
    downloader.download(url=url)
    print("start transform JSON raw file to csv file")
    doc = Document(raw_root=raw_file)
    doc.to_excel_all(tree, root=args.dest, file_type=args.type)
    print("clear")


def CLI():
    parser = argparse.ArgumentParser(
        usage="python main.py --type y --date 2000-2021 --dest data_year", description="国家数据抓取器"
    )
    parser.add_argument("--type", default="month", help="抓取哪种类型的数据，目前没用")
    parser.add_argument("--encoding", default="utf-8", help="输出的csv文件的编码,默认的UTF8可能对Excel不友好")
    parser.add_argument("--date", default="2006-2023", help="请求的数据区间如 --date 1978-2015")
    parser.add_argument("--dest", default="data_month", help="输出目录")

    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("DEBUG MODE")
        print("IF YOU WANT USE IT IN CLI, YOU NEED A ARGUMENT TO ACTIVATE IT")

        # It provide a helper varible to support debug
        class Args(object):
            def __init__(self) -> None:
                self.type = "y"
                self.encoding = "utf-8"
                self.date = "2010-2024"
                self.dest = "data_year"

        args = Args()
        run(args)
    else:
        CLI()
