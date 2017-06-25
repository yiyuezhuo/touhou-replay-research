# -*- coding: utf-8 -*-
"""
Created on Sun Jun 18 20:32:20 2017

@author: yiyuezhuo
"""

from threp import run
from utils import find_last_true, find_last_match


file = 'replay/th10_02.rpy'
raw_file = file+'.raw'
run(file)
with open('example2.txt','rb') as f:
    content1 = f.read()
with open(raw_file, 'rb') as f:
    content2 = f.read()
print(content1 == content2)

cut = find_last_match(content1, content2)
print(content1[:cut] == content2[:cut])
print(content1[:cut+1] == content2[:cut+1])
print(cut,'/',len(content1))