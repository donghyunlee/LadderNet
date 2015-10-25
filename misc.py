'''
@author: Eona
'''
import os
import sys
import json
import functools
import os.path
from os.path import join as ojoin
from os.path import isfile, isdir
import shutil
import inspect
import subprocess as pc
import collections
from time import sleep
from copy import deepcopy
from json import loads as json_parse
from json import dumps as json_str
import random


file_exists = os.path.exists


def file_time(fname):
    return str(os.path.getctime(fname))


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
        print name, '==>', eval(name,frame.f_globals,frame.f_locals)
        
        
def nohup(cmd, log_files, verbose=True, dryrun=False):
    if isinstance(log_files, str):
        outlog, errlog = log_files, '&1' # 2>&1
    else:
        outlog, errlog = log_files
        
    if dryrun:
        print 'Dry run:'
        
    cmd = 'nohup {} > {} 2>{} &'.format(cmd, outlog, errlog)
    if verbose:
        print cmd
        
    # don't actually run anything
    if dryrun:
        return

    # dollar-bang gets the PID of the last backgrounded process
    return pc.check_output(cmd + ' echo $!', shell=True).strip()


def nohup_py(cmd, *args, **kwargs):
    return nohup('python -u {}'.format(cmd), *args, **kwargs)


def kill(pid):
    if pid is None:
        return

    if isinstance(pid, list) or isinstance(pid, tuple):
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
        

def min_at(values):
    return min( (v, i) for i, v in enumerate(values) )


def max_at(values):
    return max( (v, i) for i, v in enumerate(values) )


# ========== email notification ==========
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

class Emailer(object):
    
    def __init__(self, sender_name, 
                 sender_email, 
                 recv_email, 
                 passwd,
                 smtp_addr):
        self.sender_name = sender_name
        self.sender_email = sender_email
        self.recv_email = recv_email
        self.passwd = passwd
        self.smtp_addr = smtp_addr
        
        # under debug mode, doesn't send any email
        self._debug = False
    
    
    def set_debug(self, debug):
        self._debug = debug
    

    def send_multiple(self, *messages):
        '''
        Send multiple emails.
        Each msg is a tuple (subject, bodytext)
        '''
        try:
            server = smtplib.SMTP(self.smtp_addr, 587)
            server.ehlo()
            server.starttls()
            server.login(self.sender_email, self.passwd)

            for msgtuple in messages:
                if type(msgtuple) != tuple or len(msgtuple) != 2:
                    raise Exception(
                        "Each message must be a tuple (subject, bodytext)")
                
                subject, textbody = msgtuple
                msg = MIMEText(textbody)
                
                msg['Subject'] = subject
                msg['From'] = formataddr((self.sender_name, self.sender_email))
                msg['To'] = self.recv_email
                msg = msg.as_string()
                
                if self._debug:
                    print '======== [Emailer debug msg] ========'
                    print msg
                    print '======== [end msg] ========\n'
                else:
                    server.sendmail(self.sender_email, [self.recv_email], msg)

            server.quit()

        except Exception, e:
            print '[Emailer error]:', str(e)

    def send(self, subject, textbody):
        self.send_multiple((subject, textbody))
            

if __name__ == '__main__':
    # each line corresponds to Emailer __init__ args
    email_info = map(str.strip, open('email_info.txt').readlines())
    
    emailer = Emailer(*email_info)
    emailer.set_debug(True)
    
    emailer.send_multiple(('Magic 1', 'Royal Flush'),
                          ('Magic 2', 'Infinity Typist'),
                          ('Magic 3', 'Priestess of Theano'))
