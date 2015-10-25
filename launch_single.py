'''
Automate experiment launching
'''
from misc import *
from automator import *

# fix random data seeds for semi-supervised experiments
DSEEDS = [777, 1, 405, 186, 620, 209, 172, 734, 154, 996]

KEYS = ['decoder', 'labelled', 'dseed']

GPU_FULLNAME = {
        'dam': 'Damascus',
        'pre': 'Pretoria',
        'kat': 'Kathmandu',
        'bag': 'Baghdad',
        'bud': 'Budapest',
        'lis': 'Lisbon'
}

SPEC = {}

hyper_specs = [
               (2, '0.03', 100),
               (3, '0.03', 100),
               (4, '0.05', 100),
               (5, '0.03', 100),
               
               
               (2, '0.05', 1000),
               (3, '0.03', 1000),
               (4, '0.03', 1000),
               (5, '0.03', 1000)
               ]

all_specs = []
for _a, _b, _c in hyper_specs:
    all_specs += [('fullmlp_{}_relu_rand+{}'.format(_a, _b),
                   _c,
                   _i) for _i in range(1, 10)]

# pretoria
# TODO: remove
SPEC['pre'] = [
               ('fullmlp_3_relu_rand+0.03', 100, 6), 
               ('fullmlp_3_relu_rand+0.03', 100, 7),
               ('fullmlp_3_relu_rand+0.03', 100, 8),
               ('fullmlp_3_relu_rand+0.03', 100, 9),
               ('fullmlp_4_relu_rand+0.05', 100, 1)
               ]

# kathmandu
SPEC['kat'] = [
               ]

# baghdad
SPEC['bag'] = [
               ]

# budapest
SPEC['bud'] = [
               ]

# damascus
SPEC['dam'] = [
               ]

# lisbon
SPEC['lis'] = []


for gpu in ['pre', 'kat', 'bag', 'bud', 'dam']:
    SPEC[gpu] = all_specs[:15]
    del all_specs[:15]


def gen_experiments(specs):
    expers = []
    for i, spec in enumerate(specs):
        setting = AttributeDict({k: s for k, s in zip(KEYS, spec)})

        # extra derived settings
        setting.dseed = DSEEDS[setting.dseed]
        setting.dir = '{decoder}-{labelled}@{dseed}'.format(**setting)
#         setting.dir = 'temp_{}'.format(i)
        setting.seed = random.randint(0, 100000)
        
        formatter = lambda s: s.format(**setting)
        
        command = formatter('run.py train {dir} '
            '--encoder-layers 1000-500-250-250-250-10 '
            '--decoder-spec {decoder} '
            '--denoising-cost-x 1000,10,0.1,0.1,0.1,0.1,0.1 '
            '--labeled-samples {labelled} '
            '--unlabeled-samples 60000 '
            '--num-epochs 150 '
            '--dseed {dseed} ' # shouldn't change across experiments
            '--seed {seed}')
        
        logfile = formatter('logs/{dir}.txt')
        sentinel = formatter('results/{dir}/sentinel.txt')
        
        e = Experiment(spec, command, logfile, sentinel)
        expers.append(e)
        
    return expers
    
#         pid = nohup_py('run.py train {dir} '
#             '--encoder-layers 1000-500-250-250-250-10 '
#             '--decoder-spec {decoder} '
#             '--denoising-cost-x 1000,10,0.1,0.1,0.1,0.1,0.1 '
#             '--labeled-samples {labelled} '
#             '--unlabeled-samples 60000 '
#             '--num-epochs 150 '
#             '--dseed {dseed} ' # shouldn't change across experiments
#             '--seed {seed}'.format(**setting),
#             'logs/{dir}.txt'.format(**setting),
#             dryrun=False)
    

if __name__ == '__main__':
    gpu = sys.argv[1]
    
    def gpu_subject_gen(expers):
        return datetime.now().strftime(
                    GPU_FULLNAME[gpu] + ' experiment %m/%d')

    email_info = map(str.strip, open('email_info.txt').readlines())
    emailer = Emailer(*email_info)
    email_reporter = EmailReporter(emailer,
                                   concur_email=4,
                                   subject_gen=gpu_subject_gen)
    email_trailer = open('email_trailer.txt').read().rstrip()

    expers = gen_experiments(SPEC[gpu])
    print 'Experiment queue:'
    for exper in expers:
        print exper
    
#     sys.exit(0)
    
    print '\nStarting ExperimentManager ...\n'

    ExperimentManager(expers, 
                      concur_limit=4,
                      check_period=60,
                      email_reporter=email_reporter,
                      email_trailer=email_trailer).launch()
