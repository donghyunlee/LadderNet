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
import random
from datetime import datetime
import signal


class AttributeDict(dict):
    __getattr__ = dict.__getitem__

    def __setattr__(self, a, b):
        self.__setitem__(a, b)


def min_at(values):
    return min( (v, i) for i, v in enumerate(values) )


def max_at(values):
    return max( (v, i) for i, v in enumerate(values) )


def debugprint(*varnames):
    record=inspect.getouterframes(inspect.currentframe())[1]
    frame=record[0]
    for name in varnames:
        print name, '==>', eval(name,frame.f_globals,frame.f_locals)
        
        
class PrintRedirection:
    "Context manager: temporarily redirects stdout and stderr"
    def __init__(self, stdout=sys.stdout, stderr=sys.stderr):
        self._stdout = stdout
        self._stderr = stderr
            
    def __enter__(self):
        self._old_out, self._old_err = sys.stdout, sys.stderr
        self._old_out.flush();  self._old_err.flush()
        sys.stdout, sys.stderr = self._stdout, self._stderr
            
    def __exit__(self, exc_type, exc_value, traceback):
        self._stdout.flush();   self._stderr.flush()
        # restore the normal stdout and stderr
        sys.stdout, sys.stderr = self._old_out, self._old_err
        
        
# ========== File system ==========
file_exists = os.path.exists

def file_time(fname):
    return str(os.path.getctime(fname))


# ========== JSON ==========
json_str = functools.partial(json.dumps, indent=4)

        
class JsonWriter(AttributeDict):
    def __init__(self, json_file, *args, **kwargs):
        AttributeDict.__init__(self, *args, **kwargs)
        self.update(json_load(json_file))


def json_load(filepath):
    with open(filepath, 'r') as fp:
        return json.load(fp)


def json_save(filepath, dat):
    with open(filepath, 'w') as fp:
        json.dump(dat, fp, indent=4)


# ========== Processes ==========
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


def kill(pid, signal='INT'):
    if pid is None:
        return
    
    if not isinstance(signal, str):
        signal = str(signal)

    if isinstance(pid, list) or isinstance(pid, tuple):
        for p in pid:
            kill(p)
    else:
        if not isinstance(pid, str):
            pid = str(pid)
        pc.call(['kill', '-'+signal, pid])
        
        
class SignalReceived(Exception):
    """
    Raised when any signal received
    .signum: value of the signal, symbolic
    .signame: name of the signal, string
    """
    pass


def register_signals(signames=None):
    """
    signames is a list of supported signals: SIGINT, SIGSTOP, etc.
    if None, default to register all supported signals
    """
    all_signames = filter(lambda s: (s.startswith('SIG')
                                     # not sure why ...
                                     and not s.startswith('SIGC')
                                     # OS cannot catch these two
                                     and s not in ['SIGKILL', 'SIGSTOP']
                                     and '_' not in s),
                          dir(signal))
    signum_to_name = {getattr(signal, sig): sig for sig in all_signames}

    if signames is None:
        signames = all_signames

    def _sig_handler(signum, frame):
        signame = signum_to_name[signum]
        exc = SignalReceived('{} [{}] received'.format(signame, signum))
        exc.signum = signum
        exc.signame = signame
        exc.frame = frame
        raise exc
            
    for sig in signames:
        signal.signal(getattr(signal, sig), _sig_handler)


# ========== Email API ==========
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
