import subprocess as pc
from datetime import datetime
import sys
import os.path
import time
import traceback

logs = []

fullnames = {
        'dam': 'damascus',
        'pre': 'pretoria',
        'kat': 'kathmandu',
        'bag': 'baghdad',
        'bud': 'budapest',
        'lis': 'lisbon'
}

# get cluster address
for sshstr in open('/Users/Eona/CLIC/tools/clicssh.txt'):
    pass

if sys.argv[1] == 'all':
    gpus = fullnames.keys()
    # lisbon currently down
    gpus.remove('lis')
else:
    gpus = sys.argv[1:]


# to be used in log file names
time_fname = datetime.now().strftime('%m-%d.%H:%M:%S.txt')

for gpu in gpus:
    fullgpu = fullnames[gpu]
    print 'Launching', fullgpu, '...\n'
    
    logfile = 'ainz/{}_{}'.format(gpu, time_fname)
    out = ''

    try:
        # first launch_single in nohup detached
        # sh -c is REQUIRED for nohup not to block ssh
        out = pc.check_output((sshstr.strip() + 
                " sh -c \"'cd ~/workspace/LadderNet && "
                ". ~/workspace/bin/activate && "
                "nohup python -u launch_single.py {} > {logfile} 2>&1 & "
                "sleep 2 && " # must wait before cat, not so fast to launch
                "cat ~/workspace/LadderNet/{logfile}'\"")\
                .format(fullgpu, gpu, logfile=logfile), 
            shell=True)

        print out

    except pc.CalledProcessError, e:
        traceback.print_exc()
    
    print '-' * 20

    logs.append('=============== ' + fullgpu + '===============\n' 
                + out.strip())

if not os.path.exists('ainz'):
    os.makedirs('ainz')

logfile = 'ainz/' + time_fname
print >> open(logfile, 'w'), '\n\n'.join(logs)

print 'Launch profile saved to', logfile