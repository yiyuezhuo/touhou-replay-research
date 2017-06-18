# -*- coding: utf-8 -*-
"""
Created on Sun Jun 18 11:01:46 2017

@author: yiyuezhuo
"""

#from struct import unpack,pack
from utils import signed_int
from th10 import th10decode

def run(file):
    buffer = bytearray(0x100000) # cofusing setting, it indicate some overflow error?
    with open(file, 'rb') as f:
        _buffer = f.read()
    flength = len(_buffer)
    buffer[:flength] = _buffer
    tag = signed_int(buffer, 0)
    if tag == 0x72303174: # th10
        th10decode(file, buffer, flength)

def main(argc, argv):
    if argc == 1:
        print("Usage : python {} [filename]".format(argv[0]));
    elif argc == 2:
        run(argv[1])
        
if __name__ == '__main__':
    # simple CLI interface
    import sys
    main(len(sys.argv), sys.argv)