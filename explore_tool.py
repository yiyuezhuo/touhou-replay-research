# -*- coding: utf-8 -*-
"""
Created on Sun Jun 25 16:29:50 2017

@author: yiyuezhuo
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd
import os
import pickle

def load_info(path, data_frame = True, not_equip = False, use_bool = True, int16=True):
    with open(path,encoding='utf8') as f:
        info = json.load(f)
    info['stages'] = {int(key):value for key,value in info['stages'].items()}
    if data_frame:
        stages = {}
        for key,stage in info['stages'].items():
            if use_bool:
                mat = [[True if item=='1' else False for item in record] for record in stage['replay']]
                df = pd.DataFrame(mat)
            else:
                if int16:
                    dtype = np.int16
                else:
                    dtype = np.int64 # default pandas behaviour
                mat = [[1 if item=='1' else 0 for item in record] for record in stage['replay']]
                df = pd.DataFrame(mat, dtype = dtype)
            df.columns = ['press_right','press_left','press_down','press_up',
                          'pressing_ctrl','pressing_right','pressing_left',
                          'pressing_down','pressing_up','pressing_shift',
                          'pressing_x','pressing_z']
            _stage = stage.copy()
            _stage['replay'] = df
            stages[key] = _stage
        info['stages'] = stages
    if not not_equip:
        delta_equip(info)
    return info
    
class press:
    @staticmethod
    def right(frame):
        return frame[0] == '1'
    @staticmethod
    def left(frame):
        return frame[1] == '1'
    @staticmethod
    def down(frame):
        return frame[2] == '1'
    @staticmethod
    def up(frame):
        return frame[3] == '1'

class pressing:
    @staticmethod
    def ctrl(frame):
        return frame[4] == '1'
    @staticmethod
    def right(frame):
        return frame[5] == '1'
    @staticmethod
    def left(frame):
        return frame[6] == '1'
    @staticmethod
    def down(frame):
        return frame[7] == '1'
    @staticmethod
    def up(frame):
        return frame[8] == '1'
    @staticmethod
    def shift(frame):
        return frame[9] == '1'
    @staticmethod
    def x(frame):
        return frame[10] == '1'
    @staticmethod
    def z(frame):
        return frame[11] == '1'

    
def frame_to_delta(frame, speeds = (2.0,4.5), shock_speed = 0.0):
    dx,dy = 0,0
    speed = speeds[0] if pressing.shift(frame) else speeds[1] # pixel/frame
    
    if pressing.right(frame):
        dx += speed
    if pressing.left(frame):
        dx -= speed
    if pressing.down(frame):
        dy -= speed
    if pressing.up(frame):
        dy += speed
    
    # the vague shock movement
    if press.right(frame):
        dx += shock_speed
    if press.left(frame):
        dx -= shock_speed
    if press.down(frame):
        dy -= shock_speed
    if press.up(frame):
        dy += shock_speed

    
    return dx,dy

def replay_to_xy(replay, speeds = (2.0,4.5), shock_speed = 0.0):
    length = len(replay)
    xy = np.zeros((length,2))
    x,y = 0.0,0.0
    for i,frame in enumerate(replay):
        dx,dy = frame_to_delta(frame, speeds = speeds, shock_speed = shock_speed)
        x,y = x+dx,y+dy
        xy[i,:] = x,y
    return xy
    
def plot_trace_2d(xy):
    #xy = replay_to_xy(replay)
    plt.plot(xy[:,0], xy[:,1])

def plot_trace_3d(xy):
    #xy = replay_to_xy(replay)
    t = np.arange(xy.shape[0])
    fig = plt.figure()
    ax = Axes3D(fig)
    ax.plot(xy[:,0], t, xy[:,1], label='trace')
    ax.set_xlabel('x')
    ax.set_ylabel('t')
    ax.set_zlabel('y')
    plt.legend()
    return ax

def plot_trace_sequence(xy, xlim, ylim, chunk = 600, desc = ''):
    length = xy.shape[0]
    idx = 0
    while idx < length:
        _xy = xy[idx:idx+chunk,:]
        plot_trace_2d(_xy)
        plt.xlim(*xlim)
        plt.ylim(*ylim)
        plt.title(desc + ' 2d trace {} - {}'.format(idx,idx+chunk))
        plt.show()
        ax = plot_trace_3d(_xy)
        ax.set_xlim(*xlim)
        ax.set_zlim(*ylim)
        plt.title(desc + ' 3d trace {} - {}'.format(idx,idx+chunk))
        plt.show()
        idx += chunk

def summary(info):
    print(' '.join([info['game'],info['character'],info['ctype'],info['rank'],info['clear']]))
    print('frame score')
    for i in range(info['stage']):
        stage = info['stages'][i]
        print(stage['frame'],stage['score'])
'''
def info_wrap(func = None, use_index = None):
    # ugly trick
    
    def _func(info, inplace = True):
        for i in range(info['stage']):
            stage = info['stages'][i]
            if use_index:
                res = func(i,stage['replay'])
            else:
                res = func(stage['replay'])
            if not inplace:
                stage['replay'] = res
    
    if use_index == None:
        use_index = False
        return _func
    else:
        assert func == None
        assert use_index in {True,False}
        def __func(___func):
            nonlocal func
            func = ___func
            return _func
        return __func
'''
        
def look_pressing(key, info, press = False):
    for i in range(info['stage']):
        stage = info['stages'][i]
        df = stage['replay']
        groupby = df['{}_{}'.format('press' if press else 'pressing', key)].groupby(df.index.map(lambda t: t//60))
        gs = groupby.sum()
        #gs.plot()
        plt.fill_between(np.arange(len(gs)),gs)
        plt.ylim(-1,61)
        plt.title('stage {}'.format(i+1))
        #plt.legend()
        plt.show()
        
def look_pressing_shift(info):
    look_pressing('shift', info)
    
def info_wrap(func = None, use_index = None):
    # ugly trick
    
    def _func(info, inplace = True):
        for i in range(info['stage']):
            stage = info['stages'][i]
            if use_index:
                res = func(i,stage['replay'])
            else:
                res = func(stage['replay'])
            if not inplace:
                stage['replay'] = res
    
    if use_index == None:
        use_index = False
        return _func
    else:
        assert func == None
        assert use_index in {True,False}
        def __func(___func):
            nonlocal func
            func = ___func
            return _func
        return __func

@info_wrap
def delta_equip(df):
    df['speed'] = df['pressing_shift'] * 2.0 + (1-df['pressing_shift'])*4.5
    df['dx'] = (-df['pressing_left'] + df['pressing_right'])*df['speed']
    df['dy'] = (-df['pressing_down'] + df['pressing_up'])*df['speed']
    df['move'] = np.abs(df['dx']) + np.abs(df['dy'])

@info_wrap(use_index = True)
def show_move_situation(i,df):
    df2 = df.groupby(df.index.map(lambda t:t//60)).sum()
    plt.plot(np.abs(df2['dx'])+np.abs(df2['dy']))
    plt.title('stage {} abs movment'.format(i+1))
    plt.show()
    plt.plot(df2['move']/(np.abs(df2['dx'])+np.abs(df2['dy'])+1))
    plt.title('stage {} micro movment index (with +1 smooth)'.format(i+1))
    plt.show()
    
def transform_wrap(func, name_func = None, filter = None, tast_desc = None):
    if name_func == None:
        name_func = lambda fname:fname
    if tast_desc == None:
        tast_desc = lambda path,target_path:None
    def _func(origin_dir, target_dir, verbose = 2):
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        for name in os.listdir(origin_dir):
            path = os.path.join(origin_dir, name)
            if os.path.isdir(path):
                target_path = os.path.join(target_dir, name)
                _func(path, target_path)
            else:
                target_name = name_func(name)
                target_path = os.path.join(target_dir, target_name)
                desc = tast_desc(path, target_path)
                if not filter(path):
                    continue
                if os.path.exists(target_path):
                    if verbose >= 2:
                        print('skip {}'.format(desc))
                    continue
                if verbose >= 2:
                    print('try {}'.format(desc))
                
                try:
                    func(path, target_path)
                except ValueError:
                    print('error {}'.format(desc))
                    continue
                
                if verbose >= 1:
                    print('complete {}'.format(desc))
    return _func

def cache_int16(path, target_path):
    info = load_info(path, use_bool=False, not_equip=True)
    with open(target_path,'wb') as f:
        pickle.dump(info, f)
        
def load_infos(info_dir):
    '''
    It mainly provide a more quickly and low memory cost API to load data into memory
    '''
    infos = {}
    for name in os.listdir(info_dir):
        path = os.path.join(info_dir, name)
        with open(path,'rb') as f:
            infos[name] = pickle.load(f)
    return infos
        
transform_int16 = transform_wrap(cache_int16, 
                                 name_func = lambda name:name+'.pickle',
                                 filter = lambda path:path.endswith('.rpy.json'),
                                 tast_desc = lambda path, target_path:'{} -> {}'.format(path,target_path))


def show_pressing_in_time(info_list, key, frame = True, second = 60):
    # anyway... if frame is False, we will merge second ( perhap the second should be 'frames' ... ) frame into a item
    frame_matrix = np.array([[info['stages'][i]['frame'] for i in range(6)] for info in info_list])

    if frame:
        for i,max_frame in enumerate(frame_matrix.max(axis=0)):
            arr = np.zeros(max_frame)
            for info in info_list:
                add = np.zeros(max_frame)
                ser = info['stages'][i]['replay'][key]
                pressing = ser
                add[:len(pressing)] = pressing
                arr += add
            plt.plot(arr)
            plt.title('stage {} {} count'.format(i+1, key))
            plt.show()
    else:
        for i,max_frame in enumerate(frame_matrix.max(axis=0)):
            arr = np.zeros(max_frame//second+1)
            for info in info_list:
                add = np.zeros(max_frame//second+1)
                ser = info['stages'][i]['replay'][key]
                pressing = ser.groupby(ser.index.map(lambda t:t//second)).sum()
                add[:len(pressing)] = pressing
                arr += add
            plt.plot(arr)
            plt.title('stage {} {} count ({} frame)'.format(i+1, key, second))
            plt.show()

def show_pressing_in_time2(info_list, key, key2, frame = True, second = 60):
    # anyway... if frame is False, we will merge second ( perhap the second should be 'frames' ... ) frame into a item
    frame_matrix = np.array([[info['stages'][i]['frame'] for i in range(6)] for info in info_list])
    
    keys = [key,key2]

    if frame:
        for i,max_frame in enumerate(frame_matrix.max(axis=0)):
            arr = np.zeros((2,max_frame))
            for j in range(2):
                for info in info_list:
                    add = np.zeros(max_frame)
                    ser = info['stages'][i]['replay'][keys[j]]
                    pressing = ser
                    add[:len(pressing)] = pressing
                    arr[j,:] += add
                
            plt.plot(arr[0,:],label="{}".format(keys[0]),color='b')
            plt.ylabel(keys[0],color='b')
            plt.yticks(color='b')
            plt.twinx()
            plt.plot(arr[1,:],label="{}".format(keys[1]),color='r')
            plt.ylabel(keys[1],color='r')
            plt.yticks(color='r')
            plt.title('stage {} count'.format(i+1))
            plt.show()
    else:
        for i,max_frame in enumerate(frame_matrix.max(axis=0)):
            arr = np.zeros((2,max_frame//second+1))
            for j in range(2):
                for info in info_list:
                    add = np.zeros(max_frame//second+1)
                    ser = info['stages'][i]['replay'][keys[j]]
                    pressing = ser.groupby(ser.index.map(lambda t:t//second)).sum()
                    add[:len(pressing)] = pressing
                    arr[j,:] += add
            
            plt.plot(arr[0,:],label="{}".format(keys[0]),color='b')
            plt.ylabel(keys[0],color='b')
            plt.yticks(color='b')
            plt.twinx()
            plt.plot(arr[1,:],label="{}".format(keys[1]),color='r')
            plt.ylabel(keys[1],color='r')
            plt.yticks(color='r')
            plt.title('stage {} count ({} frame)'.format(i+1, second))
            plt.show()
