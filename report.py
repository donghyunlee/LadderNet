'''
Report from logs 
'''
import sys
from os.path import join as ojoin

def parse_log(path, keyvars):
    results = {}
    for line in open(path):
        colon_index = line.find(":")
        if colon_index != -1:
            key = line[:colon_index]
            if key in keyvars:
                value = float(line[colon_index + 1:])
                if key in results:
                    results[key].append(value)
                else:
                    results[key] = [value]
                    
    return [results[key] for key in keyvars]


def min_at(values):
    return min( (v, i) for i, v in enumerate(values) )


if __name__ == '__main__':
    curves = parse_log(ojoin(sys.argv[1], 'log.txt'), 
                       ['valid_approx_cost_class_corr', 
                        'valid_approx_error_rate'])
    valid_cost, valid_i = min_at(curves[0])
    print 'epochs:\t\t', len(curves[0])
    print 'min cost:\t', valid_cost
    print 'ER at min cost:\t', curves[1][valid_i]
    print 'min ER:\t\t', min(curves[1])