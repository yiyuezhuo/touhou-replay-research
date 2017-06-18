# -*- coding: utf-8 -*-
"""
Created on Sun Jun 18 09:05:09 2017

@author: yiyuezhuo
"""

from struct import pack, unpack

def unsigned_int(_bytes, pointer):
    return unpack('I', _bytes[pointer:pointer+4])[0]
def signed_int(_bytes, pointer):
    return unpack('i', _bytes[pointer:pointer+4])[0]

def bin32(num):
    return '{0:>32}'.format(bin(num)[2:]).replace(' ','0')

class Ref(object):
    pass