'''
@author: Eona
Automate experiment launching and managing
'''

from misc import *

class Experiment(object):
    
    def __init__(self, spec, command, logfile, sentinel):
        '''
        Sentinel file contains status and other information
        1st line must be a valid state: ended, crashed, running
        2nd+ lines contain extra info. 
        Any line starting with "#" will be ignored
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
        self.info = '' # from sentinel file
    
    
    def _sentinel_info(self):
        # read status from the sentinel
        if file_exists(self.sentinel):
            contents = map(str.strip, open(self.sentinel).readlines())
            # ignore all lines starting with '#'
            info = '\n'.join(filter(lambda x: not x.startswith('#'), 
                                          contents[1:]))
            return contents[0], info
        else:
            return None, ''
        
    
    def launch(self, verbose=True, dryrun=False):
        self._pid = nohup_py(self.command, self.logfile, 
                             verbose=verbose, 
                             dryrun=dryrun)
        if verbose:
            print 'Launch {} PID = {}\n'.format(self.spec, self._pid)

        if self._pid is not None:
            self._status = 'running'
    
    
    def kill(self):
        kill(self._pid)
        if self._status in ['running']:
            self._status = 'killed'

    
    @property
    def status(self):
        if self._pid is not None:
            status, self.info = self._sentinel_info()
            if status and self._status != 'killed':
                self._status = status

        return self._status
    
    
    def is_done(self):
        return self.status in ['ended', 'crashed', 'killed']
        
    
    @property
    def pid(self):
        return self._pid
    
    
    def __str__(self):
        return str(self.spec)
    
    def __repr__(self):
        return "Exper {}".format(str(self))
#         return self.spec[0]
    
    
class EmailReporter(object):
    """
    Specify how to send email when an experiment ends
    """
    
    @staticmethod
    # lambda [Experiments]: "email subject"
    def default_subject_gen(expers):
        return '{} experiment{} ended'.format(
                    len(expers),
                    's' if len(expers) > 1 else '')
    
    # lambda [Experiments]: "email body"
    @staticmethod
    def default_bodytext_gen(expers):
        bodytxt = ['{spec} status: {status}\n\n'
                   'Info:\n{info}\n\n'
                   'Command: {command}'\
                   .format(spec=exper.spec, 
                           status=exper.status,
                           info=exper.info,
                           command=exper.command)
                   for exper in expers]
        
        return ('\n' + '='*37 + '\n\n').join(bodytxt)
    
    
    def __init__(self, emailer, 
                 concur_email=3,
                 subject_gen=None,
                 bodytext_gen=None):
        self.emailer = emailer
        # number of experiments per email report
        self.concur_email = concur_email

        if subject_gen is None:
            subject_gen=EmailReporter.default_subject_gen
        self.subject_gen = subject_gen

        if bodytext_gen is None:
            bodytext_gen=EmailReporter.default_bodytext_gen
        self.bodytext_gen = bodytext_gen
        
        self.queue = []
        
    
    def enqueue(self, exper):
        """
        Auto-send when 'concur_email' number of experiments enqueued
        """
        self.queue.append(exper)
        
        if len(self.queue) >= self.concur_email:
            self.flush_send()


    def flush_send(self):
        """
        Flush the queue and send out all items, regardless of 'concur_email'
        Do nothing when the queue is empty
        """
        if self.queue:
            self.emailer.send(self.subject_gen(self.queue),
                              self.bodytext_gen(self.queue))
            self.queue = []
        
    
class ExperimentManager(object):
    
    def __init__(self, expers, 
                 concur_limit=4, 
                 check_period=1,
                 email_reporter=None,
                 trailer_text=''):
        self.expers = expers
        # maximum number of concurrent experiments
        self.concur_limit = concur_limit
        # check per seconds
        self.check_period = check_period
        self.email_reporter = email_reporter

        # slightly hack the bodytext generator
        old_bodytext_gen = self.email_reporter.bodytext_gen
        def trailer_bodytext_gen(expers):
            body = old_bodytext_gen(expers)
            # trailer_text appended to the last email
            if self.expers[-1] in expers:
                body += '\n' + trailer_text
            return body

        self.email_reporter.bodytext_gen = trailer_bodytext_gen
        
        # experiment yet to be launched
        self.wait_queue = expers[:]
        # experiment already launched and !is_done()
        self.running_queue = []

        # finished experiments
        self.num_ended = 0
        # all experiments
        self.num_all = len(expers)
        
        
    def launch(self):
        try:
            self._launch_n(self.concur_limit)

            while self.wait_queue or self.running_queue:
                sleep(self.check_period)
                num_ended = self._update_queue()
                # keep fixed number of expers running
                self._launch_n(num_ended)
                
            # send any remaining experiment reports
            self.email_reporter.flush_send()
            
            print 'All experiments completed.'
            
        except KeyboardInterrupt:
            print '\n\nExperimentManager interrupted.'
            print 'Kill all running experiments:\n'
            for exper in self.running_queue:
                exper.kill()
                print exper.pid, 'killed'
    
    
    def _launch_n(self, num_exper):
        # launch n processes from queue head
        for exper in self.wait_queue[:num_exper]:
            exper.launch()
            self.running_queue.append(exper)
        
        del self.wait_queue[:num_exper]

    
    def _update_queue(self):
        # return number of ended expers and remove them from self.running_queue
        newqueue = []
        num_ended = 0
        for exper in self.running_queue:
            if exper.is_done():
                num_ended += 1
                print 'Exit {} with status "{}"\nInfo:\n{}\n'\
                    .format(exper, exper.status, exper.info)
                self.email_reporter.enqueue(exper)
            else:
                newqueue.append(exper)

        self.running_queue = newqueue
        return num_ended