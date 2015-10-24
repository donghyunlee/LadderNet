'''
Automate experiment launching
'''
from misc import *
import time

KEYS = ['decoder', 'labelled', 'dseed']
DSEEDS = [777, 1, 405, 186, 620, 209, 172, 734, 154, 996]

SPEC = {}

# pretoria
SPEC['pre'] = [
               ('fullmlp_2_relu_rand+0.03', 100, 1), 
               ('fullmlp_2_relu_rand+0.03', 100, 2),
               ('fullmlp_2_relu_rand+0.03', 100, 3),
               ('fullmlp_2_relu_rand+0.03', 100, 4),
               ('fullmlp_2_relu_rand+0.03', 100, 5)
               ]

# kathmandu
SPEC['kat'] = [
               ('fullmlp_2_relu_rand+0.03', 100, 6), 
               ('fullmlp_2_relu_rand+0.03', 100, 7),
               ('fullmlp_2_relu_rand+0.03', 100, 8),
               ('fullmlp_2_relu_rand+0.03', 100, 9),
               ('fullmlp_2_relu_rand+0.05', 1000, 1)
               ]

# baghdad
SPEC['bag'] = [
               ('fullmlp_2_relu_rand+0.05', 1000, 2),
               ('fullmlp_2_relu_rand+0.05', 1000, 3),
               ('fullmlp_2_relu_rand+0.05', 1000, 4),
               ('fullmlp_2_relu_rand+0.05', 1000, 5),
               ('fullmlp_2_relu_rand+0.05', 1000, 6)
               ]

# budapest
SPEC['bud'] = [
               ('fullmlp_2_relu_rand+0.05', 1000, 7),
               ('fullmlp_2_relu_rand+0.05', 1000, 8),
               ('fullmlp_2_relu_rand+0.05', 1000, 9),
               ('fullmlp_3_relu_rand+0.03', 100, 1),
               ('fullmlp_3_relu_rand+0.03', 100, 2)
               ]

# damascus
SPEC['dam'] = [
               ('fullmlp_3_relu_rand+0.03', 100, 3),
               ('fullmlp_3_relu_rand+0.03', 100, 4),
               ('fullmlp_3_relu_rand+0.03', 100, 5)
               ]

# lisbon
SPEC['lis'] = []

def automate(specs):
    for spec in specs:
        setting = AttributeDict({k: s for k, s in zip(KEYS, spec)})

        # extra derived settings
        setting.dseed = DSEEDS[setting.dseed]
        setting.dir = '{decoder}-{labelled}@{dseed}'.format(**setting)
        setting.seed = int(time.time()*100000 % 100000)
    
        pid = nohup('run.py train {dir} '
            '--encoder-layers 1000-500-250-250-250-10 '
            '--decoder-spec {decoder} '
            '--denoising-cost-x 1000,10,0.1,0.1,0.1,0.1,0.1 '
            '--labeled-samples {labelled} '
            '--unlabeled-samples 60000 '
            '--num-epochs 150 '
            '--dseed {dseed} ' # shouldn't change across experiments
            '--seed {seed}'.format(**setting),
            'logs/{dir}.txt'.format(**setting),
            dryrun=False)

        print spec, ' PID =', pid, '\n'
    

if __name__ == '__main__':
    automate(SPEC[sys.argv[1]])