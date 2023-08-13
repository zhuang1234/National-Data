import time

import requests


class TreeNode(object):
    # url = 'https://data.stats.gov.cn/easyquery.htm'
    params = {'id': 'zb', 'dbcode': 'hgyd', 'wdcode': 'zb', 'm': 'getTree'}

    def __init__(self, iid='zb', name='zb', dbcode='hgyd', data_me=None, url=None):
        self.id = iid
        self.name = name
        self.dbcode = dbcode
        self.data_me = None  # Only leaf need this field
        self.data = None
        self.children = []
        self.leaf = None
        self.url = url

    def get(self, force=False, verbose=True):
        if verbose:
            print('getting', self.id, self.name)
        if force or self.data is None:
            params = TreeNode.params.copy()
            params['id'] = self.id
            params['dbcode'] = self.dbcode
            res = requests.get(self.url, params=params, verify=False)
            self.data = res.json()
            for data in self.data:
                self.children.append(TreeNode(iid=data['id'], name=data['name'],
                                              dbcode=data['dbcode'], data_me=data))
            self.leaf = len(self.children) == 0
            time.sleep(2)

    def get_recur(self, force=False, verbose=True):
        if force or self.data is None:
            self.get(verbose=verbose)
            for child in self.children:
                child.get_recur()

    def to_dict(self):
        children = [child.to_dict() for child in self.children]
        rd = self.data.copy()
        rd['children'] = children
        return rd

    def display(self, level=0):
        print(' ' * level + self.name + ' ' + self.id)
        for child in self.children:
            child.display(level + 1)

    def get_all_pair(self):
        if self.leaf:
            return [(self.id, self.name)]
        else:
            rl = []
            for child in self.children:
                rl.extend(child.get_all_pair())
            return rl
