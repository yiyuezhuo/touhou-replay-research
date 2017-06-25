# -*- coding: utf-8 -*-
"""
Created on Mon Jun 19 19:33:44 2017

@author: yiyuezhuo
"""

import requests
from bs4 import BeautifulSoup
import os
import time
import random

url = 'http://score.royalflare.net/th10/levelchar10.html'
host = 'http://score.royalflare.net/th10/'

res = requests.get(url)
soup = BeautifulSoup(res.content,'lxml')
h3 = soup.select('h3')[3]
assert h3.text == 'Lunatic'

code_list = ['RA','RB','RC','MA','MB','MC']
table_list = []
check = h3

print('page analyzed, start download')

def try_mult_get(url):
    for i in range(10):
        try:
            return requests.get(url).content
        except ConnectionError as e:
            interval = 1+random.random()
            print('ConnectionError {} times wait {} sec'.format(i+1,interval))
            time.sleep(interval)
    raise ConnectionError

for code in code_list:
    check = check.find_next('table')
    table_list.append(check)
for code, table in zip(code_list,table_list):
    os.makedirs(code,exist_ok=True)
    for a in table.select('a'):
        surl = a.attrs['href']
        if not surl.endswith('.rpy'):
            continue
        _,name = surl.split('/')
        url = host + surl
        path = os.path.join(code, name)
        if os.path.exists(path):
            print('skip {}'.format(path))
            continue
        #content = requests.get(url).content
        content = try_mult_get(url)
        with open(path, 'wb') as f:
            f.write(content)
        print('{} -> {}'.format(url, path))
        