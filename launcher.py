import subprocess as pc
from datetime import datetime
import sys
import os.path

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

for gpu in gpus:
    fullgpu = fullnames[gpu]
    print 'Launching', fullgpu, '...\n'

    out = pc.check_output((sshstr.strip() + 
    " 'cd ~/workspace/LadderNet && "
    ". ~/workspace/bin/activate && "
    "python auto.py {}'").format(fullgpu, gpu), shell=True)
    
    print out
    print '-' * 20

    logs.append('=============== ' + fullgpu + '===============\n' 
                + out.strip())

if not os.path.exists('ainz'):
    os.makedirs('ainz')

logfile = datetime.now().strftime('ainz/%m-%d.%H:%M:%S.txt')

print >> open(logfile, 'w'), '\n\n'.join(logs)

print 'Launch profile saved to', logfile