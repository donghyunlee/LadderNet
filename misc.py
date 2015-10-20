'''
@author: Eona
'''
import os
import sys
import json
import functools
from os.path import join as ojoin
import theano as th
import theano.tensor as T
import numpy as np
import inspect
import subprocess as pc


def json_load(filepath):
    with open(filepath, 'r') as fp:
        return json.load(fp)


def json_save(filepath, dat):
    with open(filepath, 'w') as fp:
        json.dump(dat, fp, indent=4)


def debugprint(*varnames):
    record=inspect.getouterframes(inspect.currentframe())[1]
    frame=record[0]
    for name in varnames:
        print name, '==]', eval(name,frame.f_globals,frame.f_locals)
        
        
def nohup(cmd, log_files, verbose=True):
    if isinstance(log_files, str):
        outlog, errlog = log_files, '&1' # 2>&1
    else:
        outlog, errlog = log_files
        
    cmd = 'nohup python -u {} > {} 2>{} &'.format(cmd, outlog, errlog)
    if verbose:
        print cmd
        
    # dollar-bang gets the PID of the last backgrounded process
    return pc.check_output(cmd + ' echo $!', shell=True).strip()


def kill(pid):
    if not isinstance(pid, str):
        pid = str(pid)
    pc.call('kill -9 ' + pid, shell=True)


class AttributeDict(dict):
    __getattr__ = dict.__getitem__

    def __setattr__(self, a, b):
        self.__setitem__(a, b)


class JsonWriter(AttributeDict):
    def __init__(self, json_file, *args, **kwargs):
        AttributeDict.__init__(self, *args, **kwargs)
        self.update(json_load(json_file))
        