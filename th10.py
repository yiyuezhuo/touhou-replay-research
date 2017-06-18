# -*- coding: utf-8 -*-
"""
Created on Sun Jun 18 11:02:19 2017

@author: yiyuezhuo
"""

from utils import unsigned_int,bin32,bin8
from struct import unpack,pack
from common import decode,decompress
from math import ceil

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
    
def th10cut(decodedata):
    info = {'meta': decodedata[:0x64], 'stages': {}, 'stage':None}
    
    stagedata = 0x64
    stage = decodedata[0x4c]
    score = list(range(stage))
    faith = list(range(stage))
    
    for i in range(1, stage):
        stagedata += 0x1c4 + unsigned_int(decodedata, stagedata + 0x8)
        score[i - 1] = unsigned_int(decodedata, stagedata + 0xc)
        faith[i] = unsigned_int(decodedata, stagedata + 0x14)
    score[stage - 1] = unsigned_int(decodedata, 0x10)
    
    stagedata = 0x64
    
    info['stage'] = stage
    
    for l in range(stage):
        stage_info = {'score': None,'frame': None,'llength': None, 'faith':None,
                      'bin':{'header':None,'replay':None,'tail':None},
                      'index':{'header':None,'replay':None,'tail':None}}
        
        replaydata = stagedata + 0x1c4
        frame = unsigned_int(decodedata, stagedata + 0x4)
        llength = unsigned_int(decodedata, stagedata + 0x8)
        if frame * 6 + ceil(frame/30) == llength:
            pass
        elif frame* 3 + ceil(frame/60) == llength:
            frame //= 2
        else:
            raise Exception('Unknow frame pattern')
        print('score = {} | frame size = {} | stage length = {} '.format(score[l], frame, llength))
        print('void frame = {} frame ratio = {} void frame2 = {}'.format(llength - frame*6, llength / frame, llength - frame*3))

        stage_info['score'] = score[l]
        stage_info['faith'] = faith[l]
        stage_info['frame'] = frame
        stage_info['llength'] = llength
        stage_info['bin']['header'] = decodedata[stagedata : replaydata]
        stage_info['bin']['replay'] = decodedata[replaydata : (replaydata+(frame*6))]
        stage_info['bin']['tail'] = decodedata[(replaydata+(frame*6)) : (replaydata+llength)]
        stage_info['index']['header'] = (stagedata,replaydata)
        stage_info['index']['replay'] = (replaydata,(replaydata+(frame*6)))
        stage_info['index']['tail'] = ((replaydata+(frame*6)),(replaydata+llength))
        
        info['stages'][l] = stage_info
                
        stagedata += llength + 0x1c4
    
    return info
    
def th10output(decodedata):
    info = th10cut(decodedata)
    stage = info['stage']
    #score = info['score']
    #faith = info['faith']
    score = list(range(stage))
    faith = list(range(stage))
    
    output = []
    raw_output = []
    
    #stagedata = 0x64
    for l in range(stage):
        stage_info = info['stages'][l]
        
        score[l] = stage_info['score']
        faith[l] = stage_info['faith']
        
        replaydata = stage_info['bin']['replay']
        frame = stage_info['frame']
        llength = stage_info['llength']
        print('score = {} | frame size = {} | stage length = {} '.format(score[l], frame, llength))
        print('void frame = {} frame ratio = {} void frame2 = {}'.format(llength - frame*6, llength / frame, llength - frame*3))
        skey = []
        #raw_output = []
        for i in range(frame):
            if(i % 60 == 0):
                skey.append('[{0:<6}]'.format(i // 60))
            framekey = unsigned_int(replaydata, i * 6) >> 4 & 0xf
            #raw_output.append(unsigned_int(decodedata, replaydata + i * 6))
            #framekey = framekey & 0xf
            skey.append(keys[framekey])
            if((i+1) % 60 == 0):
                output.append(''.join(skey))
                skey = []
        output.append(skey)
    return output
    
def _th10output(decodedata):
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
        #print(frame)
        llength = unsigned_int(decodedata, stagedata + 0x8)
        fpsdata = replaydata + frame * 6
        # omit rank branch
        print('score = {} | frame size = {} | stage length = {} '.format(score[l], frame, llength))
        print('void frame = {} frame ratio = {} void frame2 = {}'.format(llength - frame*6, llength / frame, llength - frame*3))
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
    with open('example2.txt', 'wb') as f:
        f.write(decodedata)

        
def _th10cut(file):
    # debug helper
    from common import entry
    file, buffer, flength = entry(file)
    decodedata = th10decodedata(file, buffer, flength)
    return th10cut(decodedata)
    
def _th10decode(file):
    # debug helper
    from common import entry
    file, buffer, flength = entry(file)
    th10decode(file, buffer, flength)
    
def _show(cut_dict, limit = 30):
    # debug helper
    rd = {}
    for key,value in cut_dict.items():
        if isinstance(value,dict):
            rd[key] = _show(value, limit = limit)
        elif len(str(value)) < limit:
            rd[key] = value
        else:
            rd[key] = '...'
    return rd
    


if __name__ == '__main__':
    
    from utils import diff2
    def diff(a,b,raw = False):
        l = diff2(list(a),list(b))
        if not raw:
            print(' '.join([str(c) for c in l]))
            return
        return l
    def d(a,b,raw=False,xor = True):
        if xor:
            l = [sum([int(c) for c in bin(int(i) ^ int(j))[2:]]) for i,j in zip(a,b)]
        else:
            l = [int(i)-int(j) for i,j in zip(a,b)]
            
        if raw:
            return l
        print(l)
    
    th10_01 = _th10cut('replay/th10_01.rpy')
    th10_02 = _th10cut('replay/th10_02.rpy')
    th10_03 = _th10cut('replay/th10_03.rpy')
    th10_04 = _th10cut('replay/th10_04.rpy')
    th10_05 = _th10cut('replay/th10_05.rpy')
    th10_06 = _th10cut('replay/th10_06.rpy')
    th10_ud1990 = _th10cut('replay/th10_ud1990.rpy')
    th10_ud0e78 = _th10cut('replay/th10_ud0e78.rpy')
    h10 = th10_01['stages'][0]['bin']['header']
    h20 = th10_02['stages'][0]['bin']['header']
    h30 = th10_03['stages'][0]['bin']['header']
    h40 = th10_04['stages'][0]['bin']['header']
    h50 = th10_05['stages'][0]['bin']['header']
    h60 = th10_06['stages'][0]['bin']['header']
    h11 = th10_01['stages'][1]['bin']['header']
    h21 = th10_02['stages'][1]['bin']['header']
    h31 = th10_03['stages'][1]['bin']['header']
    h41 = th10_04['stages'][1]['bin']['header']
    h51 = th10_05['stages'][1]['bin']['header']
    h61 = th10_06['stages'][1]['bin']['header']
    t10 = th10_01['stages'][0]['bin']['tail']
    t20 = th10_02['stages'][0]['bin']['tail']
    t30 = th10_03['stages'][0]['bin']['tail']
    t11 = th10_01['stages'][1]['bin']['tail']
    t21 = th10_02['stages'][1]['bin']['tail']
    t31 = th10_03['stages'][1]['bin']['tail']
    hud19900 = th10_ud1990['stages'][0]['bin']['header']
    hud19901 = th10_ud1990['stages'][1]['bin']['header']
    hud0e780 = th10_ud0e78['stages'][0]['bin']['header']
    hud0e781 = th10_ud0e78['stages'][1]['bin']['header']
    tud19900 = th10_ud1990['stages'][0]['bin']['tail']
    tud19901 = th10_ud1990['stages'][1]['bin']['tail']
    tud0e780 = th10_ud0e78['stages'][0]['bin']['tail']
    tud0e781 = th10_ud0e78['stages'][1]['bin']['tail']