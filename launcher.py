import subprocess as pc
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
    logs.append(pc.check_output((sshstr.strip() + 
    " 'cd ~/workspace/LadderNet && "
    ". ~/workspace/bin/activate && "
    "python auto.py {}'").format(fullnames[gpu], gpu), shell=True))

print logs
