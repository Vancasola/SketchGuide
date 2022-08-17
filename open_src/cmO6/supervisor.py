from bayes_opt import BayesianOptimization
from bayes_opt.logger import JSONLogger
from bayes_opt.event import Events
from bayes_opt.util import load_logs
import numpy as np
import os
import inspect
import sys
from config import rwjson
from perform_mapper import accuracy_mapper as am
import math
from perform_mapper import resource_mapper as rm
#import skylines as sky
result = list()
param_file = "./config/params.json"
config_file = "./config/config.json"
solve_log = "./log/solve_log.json"
perform_log = "./log/perform_vectors.log"
if(os.path.exists(perform_log)):
    os.system("rm -r "+perform_log)
param_list = list()
last_compile_time = 0
last_extract_time = 0
max_metric_val = dict()

# the black-box executation environment of the P4 program
def black_box_function(reg_size, hash_cnt, hash_tbl_size, exact_tbl_size):
    # get stack frame and parse args
    frame = inspect.currentframe()
    arg_list,_,_,args = inspect.getargvalues(frame)
    params=dict()
    for x in param_list:
        params[x] = math.ceil(args[x])
    rwjson.json_write(param_file, params)
    
    metric_val = perform_mapper(params)
    
    # get the objective function (scoring function) 
    configs = rwjson.json_read(config_file) # get the configuration file
    target = 0
    global max_metric_val
    for metric, weight in configs['metrics'].items():
        target = target + metric_val[metric] / max_metric_val[metric] * weight
    print(metric_val)
    f_p = open(perform_log,"a")
    f_p.write(str(metric_val) + "\n")
    f_p.close()
    return target

# get the accuracy results and resource usage in a metric vector
def perform_mapper(params):
    # os.system('python3 accuracy_mapper.py')
    metric_val = dict()
    # get the accuracy results from the accuracy mapper
    recall, precision = am.accuracy_mapper(params['reg_size'], params['hash_cnt'], params['hash_tbl_size'], params['exact_tbl_size'])
    metric_val['recall'] = recall
    metric_val['precision'] = precision
    # reconfigure the P4 program
    rm.generate_p4(params)
    # see if the P4 program is reconfigured
    global last_compile_time, last_extract_time
    # get the resource usage from the resource mapper
    last_compile_time = rm.compile_p4(last_compile_time)
    last_extract_time, resource_usage = rm.resource_extract(last_extract_time)
    
    # extract metrics and combine 
    configs = rwjson.json_read(config_file)
    for metric, weight in configs['metrics'].items():
        if metric in resource_usage.keys():
            metric_val[metric] = resource_usage[metric]
    return metric_val

def solve_candidate(init_points,n_iter):
    configs = rwjson.json_read(config_file)
    pbounds = dict()
    # configure the parameter range of the Beyasian Optimizer
    for param,param_range in configs['params'].items():
        param_list.append(param)
        pbounds[param]=(param_range["start"],param_range["end"])
    optimizer = BayesianOptimization(
        f=black_box_function,
        pbounds=pbounds,
        verbose=2,
        random_state=1
        )
    # record the sketch skyline candidates
    logger = JSONLogger(path=solve_log)
    optimizer.subscribe(Events.OPTIMIZATION_STEP, logger)
    optimizer.maximize(
        init_points=init_points,
        n_iter=n_iter,
        kappa=10,
        xi=1e-1,
        )
    return optimizer.max

def get_max_params():
    params = dict()
    configs = rwjson.json_read(config_file)
    for param, rang in configs['params'].items():
        params[param] = rang['end']
    return params
# get the maximal metric value to normalize performance results
def get_max_metric_val():
    max_params = get_max_params()
    max_metric_val =  perform_mapper(max_params)
    max_metric_val['recall'] = 1
    max_metric_val['precision'] = 1
    return max_metric_val

def main():
    # get the maximal value of metrics to normalize performance results
    global max_metric_val
    max_metric_val = get_max_metric_val()
    # search the sketch skyline candidates
    optimized_params = solve_candidate(init_points = 10, n_iter = 40)
    return 0

if __name__ == "__main__":
    main()
