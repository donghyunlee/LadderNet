import matplotlib
# matplotlib.use('Agg')
import matplotlib.pyplot as plt
from utils import *
from report import parse_log


plt.rcParams['text.latex.preamble'] = [r"\usepackage{lmodern}"]
params = {'text.usetex': True,
          'font.size': 14,
          'font.family': 'lmodern',
          'text.latex.unicode': True}
plt.rcParams.update(params)

def pimp(xaxis='Epochs', yaxis='Cross Entropy', y_lim=None, title=None):
    plt.legend(fontsize=14)
    plt.xlabel(r'\textbf{' + xaxis + '}')
    plt.ylabel(r'\textbf{' + yaxis + '}')
    plt.grid()
    plt.title(r'\textbf{' + title + '}')
    plt.ylim(y_lim)


def plot(curves, xlabel='train', ylabel='dev', color='b',
         x_steps=None, y_steps=None):
    if len(curves) > 1:
        x, y = curves
    else:
        x = curves[0]
        y = None

    if x_steps is None:
        x_steps = range(len(x))
    if y_steps is None and y is not None:
        y_steps = range(len(y))

    plt.plot(x_steps, x, ls='-', c=color, lw=2, label=xlabel)
    if y is not None:
        plt.plot(y_steps, y, c=color, lw=2, label=ylabel)


def best(path, what='valid_Error_rate'):
    res = parse_log(path, [what])
    return min(res[what])


to_be_plotted = ['train_cost_total']
to_be_plotted = ['valid_approx_cost_class_clean']
yaxis = 'Cross Entropy'
titles = ['train ladder standard', 'valid ladder standard', 'train no bn', 'valid no bn']
main_title = 'no batch-norm'

log = ojoin(sys.argv[1], 'log.txt')
# print best(log)
results = parse_log(log, to_be_plotted)
plt.figure()
plot(results, titles[0], titles[1], 'b')

#pimp(yaxis=yaxis, y_lim=[5, 13], title=main_title)
pimp(yaxis=yaxis, y_lim=[.05, .5], title=main_title)
plt.savefig(sys.argv[2])
plt.show()

# pc.call('open ' + sys.argv[2], shell=True)