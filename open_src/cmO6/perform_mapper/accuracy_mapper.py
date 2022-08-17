import math
import sys
from perform_mapper import CountMin as Count_Min
import time as time
data_set = "./Dataset/real_len_0.txt"
param_file="./params.json"
metric_file="./metrics.json"
config_file="./config.json"

# map the accuracy results from the sketch
def accuracy_mapper(reg_size,hash_cnt,hash_tbl_size,exact_tbl_size):
    fp = open(data_set,"r")
    # configure the CM sketch
    reg_size=math.ceil(reg_size)
    hash_cnt=math.ceil(hash_cnt)
    # runtime control
    pkt_index = 0
    start_time = time.time()
    ground_truth = {}
    # initialize a CM sketch
    cm = Count_Min.CountMin(reg_size,hash_cnt,hash_tbl_size,exact_tbl_size)
    thresh = 9162
    while True:
        # extract key/value pairs from the dataset
        contain = fp.readline()
        if contain[0]=="s":
            break
        key = contain.split(' ')[0]
        pkt_len=int(contain.split(' ')[1][0:-1])
        if pkt_len == 0:
            continue
        else:
            # update sketch with the key/value pair
            cm.update(key,pkt_len,thresh)
            if key not in ground_truth:
                ground_truth.setdefault(key, 0)
            ground_truth[key] += pkt_len
            pkt_index += 1
    fp.close()
    finish_time = time.time()
    heavy_key_list=list()

    # detect the heavy hitters
    for key,val in ground_truth.items():
        if val>thresh:
            heavy_key_list.append(key)
    cm_heavy_key_list=cm.detect_heavy_hitter(thresh)
    
    # calculate the accuracy result
    recall=0
    precision=0
    f1_score=0
    for key in heavy_key_list:
        if key in cm_heavy_key_list:
            recall+=1
    if(len(heavy_key_list)):
        recall=recall/len(heavy_key_list)
    else:
        recall=1

    for key in cm_heavy_key_list:
        if key in heavy_key_list:
            precision+=1
    if(len(cm_heavy_key_list)):
        precision=precision/len(cm_heavy_key_list)
    else:
        precision=1
    f1_score=2*recall*precision/(recall+precision)

    print(recall,precision)

    #cnt_num=reg_size*hash_cnt
    cm.clear()
    return recall,precision

