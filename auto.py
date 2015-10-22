'''
Automate experiment launching
'''
from misc import *
import time

KEYS = ['decoder', 'labelled']

SPEC = {}

# pretoria
SPEC['pre'] = [
               ('fullmlp_2_relu_rand+0.03', '100'), 
               ('fullmlp_2_relu_rand+0.05', '100'), 
               ('fullmlp_2_relu_rand+0.03', '1000'), 
               ('fullmlp_2_relu_rand+0.05', '1000')
               ]

# kathmandu
SPEC['kat'] = [
               ('fullmlp_3_relu_rand+0.03', '100'), 
               ('fullmlp_3_relu_rand+0.05', '100'), 
               ('fullmlp_3_relu_rand+0.03', '1000'), 
               ('fullmlp_3_relu_rand+0.05', '1000')
               ]

# baghdad
SPEC['bag'] = [
               ('fullmlp_3_relu_zeroone', '100'), 
               ('fullmlp_3_relu_zeroone', '1000')
               ]

# budapest
SPEC['bud'] = [
               ('fullmlp_4_relu_rand+0.03', '100'), 
               ('fullmlp_4_relu_rand+0.05', '100'), 
               ('fullmlp_4_relu_rand+0.03', '1000'), 
               ('fullmlp_4_relu_rand+0.05', '1000')
               ]

# damascus
SPEC['dam'] = [
               ('fullmlp_2_relu_onezero', '100'), 
               ('fullmlp_2_relu_onezero', '1000')
               ]

# lisbon
SPEC['lis'] = []

def automate(specs):
    for spec in specs:
        setting = AttributeDict({k: s for k, s in zip(KEYS, spec)})

        # extra derived settings
        setting.dir = setting.decoder + '-' + setting.labelled
        setting.seed = int(time.time()*100000 % 100000)
    
        pid = nohup('run.py train {dir} '
            '--encoder-layers 1000-500-250-250-250-10 '
            '--decoder-spec {decoder} '
            '--denoising-cost-x 1000,10,0.1,0.1,0.1,0.1,0.1 '
            '--labeled-samples {labelled} '
            '--unlabeled-samples 60000 '
            '--num-epochs 150 '
            '--dseed 777 ' # shouldn't change across experiments
            '--seed {seed}'.format(**setting),
            'logs/{dir}.txt'.format(**setting))

        print spec, ' PID =', pid, '\n'
    

if __name__ == '__main__':
    automate(SPEC[sys.argv[1]])