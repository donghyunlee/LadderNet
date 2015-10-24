'''
@author: Eona
'''
import os
import sys
import json
import functools
import os.path
from os.path import join as ojoin
import numpy as np
import inspect
import subprocess as pc
import collections
from time import sleep


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
    if pid is None:
        return
    
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
        
