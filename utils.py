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
def bin8(num):
    return '{0:>8}'.format(bin(num)[2:]).replace(' ','0')


class Ref(object):
    pass

def diff2(s1, s2):
    import difflib
    # It include inplace modify.
    
    #s1 = [w.strip() for w in A.split(' ') if len(w.strip())>0]
    #s2 = [w.strip() for w in B.split(' ') if len(w.strip())>0]
    
    matcher = difflib.SequenceMatcher(None, s1, s2)
    #ratio = matcher.ratio()
    
    rl = []
    for tag, i1, i2, j1, j2 in reversed(matcher.get_opcodes()):
        #print(tag, i1, i2, j1, j2)
        if tag == 'delete':
            rl = ['[-'] + s1[i1:i2] + ['-]'] + rl
            del s1[i1:i2]
        elif tag == 'equal':
            rl = s1[i1:i2] + rl
        elif tag == 'insert':
            rl =  ['[+'] + s2[j1:j2] + ['+]'] + rl
            s1[i1:i2] = s2[j1:j2]
        elif tag == 'replace':
            rl = ['['] + s1[i1:i2] + ['->'] + s2[j1:j2] + [']'] + rl
            s1[i1:i2] = s2[j1:j2]
    return rl
