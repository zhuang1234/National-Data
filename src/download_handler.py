import time
import requests
import os


class Downloader(object):
    def __init__(self, tree, raw_root='raw', dbcode='hgyd', date='2020-2021'):
        self.dbcode = dbcode
        self.tree = tree
        self.map_name = dict(tree.get_all_pair())
        self.map_json = {}
        self.raw_root = raw_root
        self.date = date
        self.url = None

    def get_params(self, valuecode):
        params = dict(m='QueryData', dbcode='hgyd', rowcode='zb', colcode='sj', wds=[],
                      dfwds=[{'wdcode': 'zb', 'valuecode': None},
                             {'wdcode': 'sj', 'valuecode': self.date}], k1=None)
        # requests can't deal tuple,list,dict correctly,I transform
        # them to string and replace ' -> " to solve it
        params['dbcode'] = self.dbcode
        params['dfwds'][0]['valuecode'] = str(valuecode)  # Shocked!requests can't handle unicode properly  # noqa: E501
        params['k1'] = int(time.time() * 1000)
        rp = {key: str(value).replace("'", '"')
              for key, value in params.items()}
        return rp

    def download_once(self, valuecode, to_json=False):
        # url = 'https://data.stats.gov.cn/easyquery.htm'
        params = self.get_params(valuecode)
        res = requests.get(self.url, params=params, verify=False)
        time.sleep(2)
        if to_json:
            return res.json()
        else:
            return res.content

    def valuecode_path(self, valuecode):
        return os.path.join(self.raw_root, valuecode)

    def cache(self, valuecode, content):
        '''
        f=open(self.valuecode_path(valuecode),'wb')
        f.write(content)
        f.close()
        '''
        with open(self.valuecode_path(valuecode), 'wb') as f:
            f.write(content)

    def is_exists(self, valuecode, to_json=False):
        if to_json:
            # return self.map_json.has_key(valuecode)
            if valuecode in self.map_json:
                return True
            else:
                return False
        else:
            path = os.path.join(self.raw_root, valuecode)
            return os.path.isfile(path)

    def download(self, verbose=True, to_json=False,url=None): 
        self.url = url
        length = len(self.map_name)
        for index, valuecode in enumerate(self.map_name.keys()):
            if verbose:
                print('get data', valuecode, self.map_name[valuecode], 'clear', float(index) / length)  # noqa: E501
            if not self.is_exists(valuecode, to_json=to_json):
                res_obj = self.download_once(valuecode, to_json=to_json)
                if to_json:
                    self.map_json[valuecode] = res_obj
                else:
                    self.cache(valuecode, res_obj)
