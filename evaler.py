'''
@author: Eona
Mass evaluation
'''

from misc import *
from launch_single import DSEEDS
import numpy as np

ers = np.zeros(10, dtype=np.float32)

for i, dseed in enumerate(DSEEDS[1:]):
    d = 'results/fullmlp_2_relu_rand+0.05-1000@{}'.format(dseed)
    output = pc.check_output('python run.py evaluate ' + d, shell=True)
    ers[i] = float(output.strip().split('\n')[-1].split(':')[-1].strip())
    print dseed, 'ER =', ers[i]

print 'Mean ER =', np.mean(ers)
print 'SE =', np.std(ers) / np.sqrt(10)