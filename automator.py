'''
@author: Eona
Automate experiment launching and managing
'''

from misc import *

class Experiment(object):
    
    def __init__(self, spec, command, logfile, sentinel):
        '''
        Sentinel file contains status information
        '''
        self.spec = spec
        self.command = command
        self.logfile = logfile
        self.sentinel = sentinel
        # clear the sentinel file
        if file_exists(sentinel):
            os.remove(sentinel)

        self._pid = None
        self._status = 'null'
    
    
    def _sentinel_info(self):
        # read status from the sentinel
        if file_exists(self.sentinel):
            return open(self.sentinel).read().strip()
        else:
            return None
        
    
    def launch(self, verbose=True, dryrun=False):
        self._pid = nohup_py(self.command, self.logfile, 
                             verbose=verbose, 
                             dryrun=dryrun)
        if self._pid is not None:
            self._status = 'running'
    
    
    def kill(self):
        kill(self._pid)
        if self._status in ['running']:
            self._status = 'killed'

    
    @property
    def status(self):
        sentinel_info = self._sentinel_info()
        if sentinel_info and self._status != 'killed':
            self._status = sentinel_info

        return self._status
    
    
    def is_done(self):
        return self._status in ['ended', 'crashed', 'killed']
        
    
    @property
    def pid(self):
        return self._pid
    
    
class ExperimentManager(object):
    
    def __init__(self, experiments):
        self.experiments = experiments
        # experiment queue
        self.queue = experiments[:]
        
    
    
    