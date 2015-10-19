import matplotlib
# matplotlib.use('Agg')
import matplotlib.pyplot as plt
from utils import *


plt.rcParams['text.latex.preamble'] = [r"\usepackage{lmodern}"]
params = {'text.usetex': True,
          'font.size': 14,
          'font.family': 'lmodern',
          'text.latex.unicode': True}
plt.rcParams.update(params)


def parse_log(path, to_be_plotted):
    results = {}
    for line in open(path):
        colon_index = line.find(":")
        enter_index = line.find("\n")
        if colon_index != -1:
            key = line[:colon_index]
            value = line[colon_index + 1: enter_index]
            if key in to_be_plotted:
                values = results.get(key)
                if values is None:
                    results[key] = [value]
                else:
                    results[key] = results[key] + [value]
    return [results[key] for key in to_be_plotted]


def pimp(path=None, xaxis='Epochs', yaxis='Cross Entropy', title=None):
    plt.legend(fontsize=14)
    plt.xlabel(r'\textbf{' + xaxis + '}')
    plt.ylabel(r'\textbf{' + yaxis + '}')
    plt.grid()
    plt.title(r'\textbf{' + title + '}')
    plt.ylim([0, 0.5])
    if path is not None:
        plt.savefig(path)
    else:
        plt.show()


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

    plt.plot(x_steps, x, ls=':', c=color, lw=2, label=xlabel)
    if y is not None:
        plt.plot(y_steps, y, c=color, lw=2, label=ylabel)


def best(path, what='valid_Error_rate'):
    res = parse_log(path, [what])
    return min(res[what])


to_be_plotted = ['train_cost_class_clean']
yaxis = 'Cross Entropy'
titles = ['train ladder standard', 'valid ladder standard', 'train no bn', 'valid no bn']
main_title = 'no batch-norm'

log = ojoin(sys.argv[1], 'log.txt')
# print best(log)
results = parse_log(log, to_be_plotted)
plt.figure()
plot(results, titles[0], titles[1], 'b')

pimp(path=None, yaxis=yaxis, title=main_title)
plt.savefig(ojoin(sys.argv[1], 'plot.png'))
