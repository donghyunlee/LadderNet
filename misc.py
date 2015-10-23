'''
@author: Eona
'''
import os
import sys
import json
import functools
import os.path
from os.path import join as ojoin
import theano as th
import theano.tensor as T
import numpy as np
import inspect
import subprocess as pc
import collections


file_exists = os.path.isfile


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
        
        
def nohup(cmd, log_files, verbose=True, dryrun=False):
    if isinstance(log_files, str):
        outlog, errlog = log_files, '&1' # 2>&1
    else:
        outlog, errlog = log_files
        
    if dryrun:
        print 'Dry run:'
        
    cmd = 'nohup python -u {} > {} 2>{} &'.format(cmd, outlog, errlog)
    if verbose:
        print cmd
        
    # don't actually run anything
    if dryrun:
        return

    # dollar-bang gets the PID of the last backgrounded process
    return pc.check_output(cmd + ' echo $!', shell=True).strip()


def kill(pid):
    if isinstance(pid, collections.Iterable):
        for p in pid:
            kill(p)
    else:
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
        
        
# =========== Theano specific ===========
Trelu = lambda x: T.maximum(0, x)

Tleakyrelu = lambda x: T.switch(x > 0., x, 0.1 * x)

Tsoftplus = lambda x: T.log(1. + T.exp(x))

Tsigmoid = lambda x: T.nnet.sigmoid(x)

Tsoftmax = lambda x: T.nnet.softmax(x)

def Tnonlinear(name, x):
    act = {'relu': Trelu,
     'sig': Tsigmoid,
     'sigmoid': Tsigmoid,
     'leakyrelu': Tleakyrelu,
     'softplus': Tsoftplus,
     'softmax': Tsoftmax}.get(name)

    assert act, 'unknown nonlinearity: ' + name
    if name == 'softmax':
        x = x.flatten(2)
    return act(x)