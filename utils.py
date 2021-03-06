import os
from misc import *

import logging
import theano
from pandas import DataFrame, read_hdf

from blocks.extensions import Printing, SimpleExtension
from blocks.main_loop import MainLoop
from blocks.roles import add_role

logger = logging.getLogger('main.utils')

# ============== My addition ==============
import theano as th
import theano.tensor as T
import numpy as np

Trelu = lambda x: T.maximum(0, x)

Tleakyrelu = lambda x: T.switch(x > 0., x, 0.1 * x)

Tsoftplus = lambda x: T.log(1. + T.exp(x))

Tsigmoid = lambda x: T.nnet.sigmoid(x)

Tsoftmax = lambda x: T.nnet.softmax(x)

def Tnonlinear(name, x):
    act = {'relu': Trelu,
     'sig': Tsigmoid,
     'sigmoid': Tsigmoid,
     'leakyrelu': Tleakyrelu,
     'softplus': Tsoftplus,
     'softmax': Tsoftmax}.get(name)

    assert act, 'unknown nonlinearity: ' + name
    if name == 'softmax':
        x = x.flatten(2)
    return act(x)


class SentinelWhenFinish(SimpleExtension):
    """
    When finished, write out to a sentinel file.
    Also save all monitored variable history to json
    """
    def __init__(self, save_dir, global_history, **kwargs):
        kwargs['after_training'] = True
        super(SentinelWhenFinish, self).__init__(**kwargs)
        self.sentinel = ojoin(save_dir, 'sentinel.txt')
        self.global_history = global_history


    def do(self, which_callback, *args):
        sentinel = open(self.sentinel, 'w')
        print >> sentinel, 'ended'
        print >> sentinel, '#\n# validation report:'

        info = AttributeDict()
        costs = self.global_history['valid_approx_cost_class_corr']
        ers = self.global_history['valid_approx_error_rate']

        info.epochs = len(costs)
        info.min_cost, min_i = min_at(costs)
        info.ER_at_min_cost = ers[min_i]
        info.min_ER = min(ers)
        
        print >> sentinel, json_str(info)
        sentinel.close()
# ==================================================


def shared_param(init, name, cast_float32, role, **kwargs):
    if cast_float32:
        v = np.float32(init)
    p = theano.shared(v, name=name, **kwargs)
    add_role(p, role)
    return p


class DummyLoop(MainLoop):
    def __init__(self, extensions):
        return super(DummyLoop, self).__init__(algorithm=None,
                                               data_stream=None,
                                               extensions=extensions)

    def run(self):
        for extension in self.extensions:
            extension.main_loop = self
        self._run_extensions('before_training')
        self._run_extensions('after_training')


# class ShortPrinting(Printing):
#     def __init__(self, to_print, use_log=True, **kwargs):
#         self.to_print = to_print
#         self.use_log = use_log
#         super(ShortPrinting, self).__init__(**kwargs)
# 
#     def do(self, which_callback, *args):
#         log = self.main_loop.log
# 
#         # Iteration
#         msg = "e {}, i {}:".format(
#             log.status['epochs_done'],
#             log.status['iterations_done'])
# 
#         # Requested channels
#         items = []
#         for k, vars in self.to_print.iteritems():
#             for shortname, vars in vars.iteritems():
#                 if vars is None:
#                     continue
#                 if type(vars) is not list:
#                     vars = [vars]
# 
#                 s = ""
#                 for var in vars:
#                     try:
#                         name = k + '_' + var.name
#                         val = log.current_row[name]
#                     except:
#                         continue
#                     try:
#                         s += ' ' + ' '.join(["%.3g" % v for v in val])
#                     except:
#                         s += " %.3g" % val
#                 if s != "":
#                     items += [shortname + s]
#         msg = msg + ", ".join(items)
#         if self.use_log:
#             logger.info(msg)
#         else:
#             print msg


class SaveParams(SimpleExtension):
    """Finishes the training process when triggered."""
    def __init__(self, early_stop_var, model, save_path, **kwargs):
        super(SaveParams, self).__init__(**kwargs)
        self.early_stop_var = early_stop_var
        self.save_path = save_path
        params_dicts = model.params
        self.params_names = params_dicts.keys()
        self.params_values = params_dicts.values()
        self.to_save = {}
        self.best_value = None
        self.add_condition('after_training', self.save)
        self.add_condition('on_interrupt', self.save)
        self.add_condition('after_epoch', self.do)

    def save(self, which_callback, *args):
        to_save = {}
        for p_name, p_value in zip(self.params_names, self.params_values):
            to_save[p_name] = p_value.get_value()
        path = self.save_path + '/trained_params'
        np.savez_compressed(path, **to_save)

    def do(self, which_callback, *args):
        if self.early_stop_var is None:
            return
        val = self.main_loop.log.current_row[self.early_stop_var]
        if self.best_value is None or val < self.best_value:
            self.best_value = val
            to_save = {}
            for p_name, p_value in zip(self.params_names, self.params_values):
                to_save[p_name] = p_value.get_value()
            path = self.save_path + '/trained_params_best'
            np.savez_compressed(path, **to_save)


# class SaveParams(SimpleExtension):
#     """Finishes the training process when triggered."""
#     def __init__(self, trigger_var, params, save_path, **kwargs):
#         super(SaveParams, self).__init__(**kwargs)
#         if trigger_var is None:
#             self.var_name = None
#         else:
#             self.var_name = trigger_var[0] + '_' + trigger_var[1].name
#         self.save_path = save_path
#         self.params = params
#         self.to_save = {}
#         self.best_value = None
#         self.add_condition('after_training', self.save)
#         self.add_condition('on_interrupt', self.save)
# 
#     def save(self, which_callback, *args):
#         if self.var_name is None:
#             self.to_save = {v.name: v.get_value() for v in self.params}
#         path = self.save_path + '/trained_params'
#         logger.info('Saving to %s' % path)
#         np.savez_compressed(path, **self.to_save)
# 
#     def do(self, which_callback, *args):
#         if self.var_name is None:
#             return
#         val = self.main_loop.log.current_row[self.var_name]
#         if self.best_value is None or val < self.best_value:
#             self.best_value = val
#         self.to_save = {v.name: v.get_value() for v in self.params}


class SaveExpParams(SimpleExtension):
    def __init__(self, experiment_params, dir, **kwargs):
        super(SaveExpParams, self).__init__(**kwargs)
        self.dir = dir
        self.experiment_params = experiment_params

    def do(self, which_callback, *args):
        df = DataFrame.from_dict(self.experiment_params, orient='index')
        df.to_hdf(os.path.join(self.dir, 'params'), 'params', mode='w',
                  complevel=5, complib='blosc')


# class SaveLog(SimpleExtension):
#     def __init__(self, dir, show=None, **kwargs):
#         super(SaveLog, self).__init__(**kwargs)
#         self.dir = dir
#         self.show = show if show is not None else []
# 
#     def do(self, which_callback, *args):
#         df = self.main_loop.log.to_dataframe()
#         df.to_hdf(os.path.join(self.dir, 'log'), 'log', mode='w',
#                   complevel=5, complib='blosc')

class SaveLog(SimpleExtension):
    def __init__(self, save_dir, global_history, **kwargs):
        super(SaveLog, self).__init__(**kwargs)
        self.save_dir = save_dir
        self.global_history = global_history

    def do(self, which_callback, *args):
        epoch = self.main_loop.status['epochs_done']
        current_row = self.main_loop.log.current_row
        logger.info("\nIter:%d" % epoch)
        for var in current_row:
            varstr = str(var)
            value = float(current_row[var])
            if varstr in self.global_history:
                self.global_history[varstr].append(value)
            else:
                self.global_history[varstr] = [value]

            logger.info('{}:{:.7g}'.format(varstr, value))
        
        # Save all monitored vars to json file
        json_save(ojoin(self.save_dir, 'monitor.json'), self.global_history)


def prepare_dir(save_to, results_dir='results', override=True):
    base = os.path.join(results_dir, save_to)
    i = 0

    name = base
    if override:
        if file_exists(name):
            shutil.rmtree(name)

        os.makedirs(name)
    else:
        while True:
            if i > 0:
                name = '{}.{}'.format(base, i)

            if file_exists(name):
                i += 1
            else:
                os.makedirs(name)
                break

    return name


def load_df(dirpath, filename, varname=None):
    varname = filename if varname is None else varname
    fn = os.path.join(dirpath, filename)
    return read_hdf(fn, varname)


def filter_funcs_prefix(d, pfx):
    pfx = 'cmd_'
    fp = lambda x: x.find(pfx)
    return {n[fp(n) + len(pfx):]: v for n, v in d.iteritems() if fp(n) >= 0}
