# -*- coding: utf-8 -*-
"""
Created on Sun Jun 18 11:02:19 2017

@author: yiyuezhuo
"""

from utils import unsigned_int
from struct import unpack,pack
from common import decode,decompress

_keys = [ 0xf0a1, 0xfca1, 0xfda1, 0xfda1, 0xfba1, 0x49a8, 0x4ca8, 0x49a8, 0xfaa1, 0x4aa8, 0x4ba8, 0x4aa8, 0xfba1, 0x49a8, 0x4ca8, 0x49a8 ]
keys = [pack('I',key).decode('gbk')[0] for key in _keys]


def th10decodedata(file, buffer, flength):
    length = unsigned_int(buffer, 0x1c)
    dlength = unsigned_int(buffer, 0x20)
    decodedata = bytearray(dlength)
    rawdata = bytearray(buffer[0x24:])
    
    decode(rawdata, flength, 0x400, 0xaa, 0xe1)
    decode(rawdata, flength, 0x80, 0x3d, 0x7a)
    #rlength = decompress(rawdata, decodedata, length)
    decompress(rawdata, decodedata, length)

    return decodedata
    
def th10output(decodedata):
    stagedata = 0x64
    stage = decodedata[0x4c]
    score = list(range(stage))
    faith = list(range(stage))
    for i in range(1, stage):
        #stagedata += 0x1c4 + decodedata[stagedata + 0x8]
        #score[i - 1] = decodedata[stagedata + 0xc]
        stagedata += 0x1c4 + unsigned_int(decodedata, stagedata + 0x8)
        score[i - 1] = unsigned_int(decodedata, stagedata + 0xc)
        faith[i] = unsigned_int(decodedata, stagedata + 0x14)
    score[stage - 1] = unsigned_int(decodedata, 0x10)
    character = decodedata[0x50]
    ctype = decodedata[0x54]
    rank = decodedata[0x58]
    clear = decodedata[0x5c]
    
    output = []
    raw_output = []
    
    stagedata = 0x64
    for l in range(stage):
        replaydata = stagedata + 0x1c4
        frame = unsigned_int(decodedata, stagedata + 0x4)
        llength = unsigned_int(decodedata, stagedata + 0x8)
        fpsdata = replaydata + frame * 6
        # omit rank branch
        print('score = {} | frame size = {} | stage length = {}'.format(score[l], frame, llength))
        skey = []
        raw_output = []
        for i in range(frame):
            if(i % 60 == 0):
                skey.append('[{0:<6}]'.format(i // 60))
            '''
            framekey
            
            '''
            framekey = unsigned_int(decodedata, replaydata + i * 6) >> 4 & 0xf
            raw_output.append(unsigned_int(decodedata, replaydata + i * 6))
            #framekey = framekey & 0xf
            skey.append(keys[framekey])
            if((i+1) % 60 == 0):
                output.append(''.join(skey))
                skey = []
        output.append(skey)
        stagedata += llength + 0x1c4
    return output

    

def th10decode(file, buffer, flength):
    decodedata = th10decodedata(file, buffer, flength)
    output = th10output(decodedata)
    with open('example.txt', 'w') as f:
        f.write('\n'.join([''.join(row) for row in output]))
