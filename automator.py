'''
@author: Eona
Automate experiment launching and managing
'''

from misc import *

class Experiment(object):
    
    def __init__(self, spec, command, logfile, sentinel):
        self.spec = spec
        self.command = command
        self.logfile = logfile
        self.sentinel = sentinel

        self._pid = None
        self._status = 'null'
        self._last_sentinel = self._sentinel_info()
    
    
    def _sentinel_info(self):
        if file_exists(self.sentinel):
            return str(os.path.getctime(self.sentinel))
        else:
            return 'nonexist'
        
    
    def check_update_status(self):
        '''
        sentinel_info change or not
        '''
        sentinel_info = self._sentinel_info()
        if self._last_sentinel != sentinel_info:
            self._last_sentinel = sentinel_info
            self._status = 'ended'
            return True
        else:
            return False
    
    
    def launch(self, verbose=True, dryrun=False):
        self._pid = nohup(self.command, self.logfile, verbose, dryrun)
        if self._pid is not None:
            self._status = 'running'
    
    
    def kill(self):
        kill(self._pid)

    
    @property
    def status(self):
        return self._status
        
    
    @property
    def pid(self):
        return self._pid