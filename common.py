# -*- coding: utf-8 -*-
"""
Created on Sun Jun 18 08:31:24 2017

@author: yiyuezhuo
"""

from utils import unsigned_int,Ref


def get_bit(buffer, ref_pointer, ref_filter, length):
    result = 0
    current = buffer[ref_pointer.value]
    for i in range(length):
        result <<= 1
        if current & ref_filter.value:
            result |= 0x1
        ref_filter.value >>= 1
        if ref_filter.value == 0:
            ref_pointer.value += 1
            current = buffer[ref_pointer.value]
            ref_filter.value = 0x80
    return result
    
def decompress(buffer, decode, length):
    ref_pointer = Ref()
    ref_pointer.value = 0
    ref_filter = Ref()
    ref_filter.value = 0x80
    dest = 0
    dict = [0 for i in range(0x2010)]
    while ref_pointer.value < length:
        bits = get_bit(buffer, ref_pointer, ref_filter, 1)
        if ref_pointer.value >= length:
            return dest
        if bits:
            bits = get_bit(buffer, ref_pointer, ref_filter, 8)
            if ref_pointer.value >= length:
                return dest
            decode[dest] = bits # decode[dest] = (unsigned char) bits;
            dict[dest & 0x1fff] = bits # dict[dest & 0x1fff] = (unsigned char) bits;
            dest += 1
        else:
            bits = get_bit(buffer, ref_pointer, ref_filter, 13)
            if ref_pointer.value >= length:
                return dest
            index = bits - 1
            bits = get_bit(buffer, ref_pointer, ref_filter, 4)
            if ref_pointer.value >= length:
                return dest
            bits += 3
            for i in range(bits):
                dict[dest & 0x1fff] = dict[index + i]
                decode[dest] = dict[index + i]
                dest += 1
    return dest
    
def decode(buffer, length, block_size, base, add):
    # buffer should be a bytearray instead of bytes
    assert isinstance(buffer, bytearray)
    tbuf = buffer.copy()
    p = 0
    left = length
    if left % block_size < block_size // 4:
        left -= left % block_size
    left -= length & 1
    while left:
        if left < block_size:
            block_size = left
        tp1 = p + block_size - 1
        tp2 = p + block_size - 2
        hf = (block_size + (block_size & 0x1)) // 2
        for i in range(hf):
            buffer[tp1] = tbuf[p] ^ base
            base = (base + add) % 0x100
            tp1 -= 2
            p += 1
        hf = block_size // 2
        for i in range(hf):
            buffer[tp2] = tbuf[p] ^ base
            base = (base + add) % 0x100
            tp2 -= 2
            p += 1
        left -= block_size
        
def entry(file):
    buffer = bytearray(0x100000) # cofusing setting, it indicate some overflow error?
    with open(file, 'rb') as f:
        _buffer = f.read()
    flength = len(_buffer)
    buffer[:flength] = _buffer
    return file, buffer, flength

        
def test(path):
    with open(path, 'rb') as f:
        buffer = f.read()
    flength = len(buffer)
    length = unsigned_int(buffer, 0x1c)
    dlength = unsigned_int(buffer, 0x20)
    decodedata = bytearray(dlength)
    rawdata = bytearray(buffer[0x24:])
    decode(rawdata, flength, 0x400, 0xaa, 0xe1)
    decode(rawdata, flength, 0x80, 0x3d, 0x7a)
    rlength = decompress(rawdata, decodedata, length)
    print(rlength)
    return decodedata

if __name__ == '__main__':
    
    #decodedata = test('replay/th10_02.rpy')
    path = 'replay/th10_02.rpy'
    buffer = bytearray(0x100000) # cofusing setting, it indicate some overflow error?
    with open(path, 'rb') as f:
        _buffer = f.read()
    flength = len(_buffer)
    buffer[:flength] = _buffer
    length = unsigned_int(buffer, 0x1c)
    dlength = unsigned_int(buffer, 0x20)
    decodedata = bytearray(dlength)
    rawdata = bytearray(buffer[0x24:])
    
    with open('replay/th10_02.rpy.raw', 'rb') as f:
        decodedata2 = f.read()
    
    with open('replay/th10_02.rpy.raw.rawdata1', 'rb') as f:
        rawdata1 = f.read()
    with open('replay/th10_02.rpy.raw.rawdata2', 'rb') as f:
        rawdata2 = f.read()
    with open('replay/th10_02.rpy.raw.rawdata3', 'rb') as f:
        rawdata3 = f.read()

    assert rawdata == rawdata1
    decode(rawdata, flength, 0x400, 0xaa, 0xe1)
    assert rawdata == rawdata2
    decode(rawdata, flength, 0x80, 0x3d, 0x7a)
    assert rawdata == rawdata3
    rlength = decompress(rawdata, decodedata, length)
    assert decodedata == decodedata2
