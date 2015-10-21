import subprocess as pc
from datetime import datetime
import sys

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

for gpu in sys.argv[1:]:
    fullgpu = fullnames[gpu]
    print 'Launching', fullgpu, '...\n'

    out = pc.check_output((sshstr.strip() + 
    " 'cd ~/workspace/LadderNet && "
    ". ~/workspace/bin/activate && "
    "python auto.py {}'").format(fullgpu, gpu), shell=True)
    
    print out
    print '-' * 20

    logs.append(fullgpu + '\n' + out.strip())


logfile = datetime.now().strftime('ainz_%m-%d.%H:%M:%S.txt')

print >> open(logfile, 'w'), '\n\n'.join(logs)

print 'Launch profile saved to', logfile