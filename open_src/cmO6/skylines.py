from config import rwjson
from perform_mapper import accuracy_mapper as am
import math
def candidate_extract(solve_log, perform_vec):
    candidates = list()
    f_s = open(solve_log,"r")
    f_p = open(perform_vec,"r")
    while(True):
        x = f_s.readline()
        if(len(x)<5):
            break
        tmp = open("tmp.json","w")
        tmp.write(x)
        tmp.close()
        tmp = open("tmp.json","r")
        x = rwjson.json.load(tmp)
        tmp.close()
        param = x['params']
        for k, v in param.items():
        	param[k] = math.ceil(v)
        target = x['target']
        x = f_p.readline()
        x = x.replace("\'","\"")
        tmp = open("tmp.json","w")
        tmp.write(x)
        tmp.close()
        tmp = open("tmp.json","r")
        #print(tmp.read())
        x = rwjson.json.load(tmp)
        per_vec = dict(x)
        candidates.append({'target': target, 'params':param, 'metrics': per_vec})
    f_s. close()
    return candidates

def dominate(a,b):
    dimension = len(a['metrics'])
    for metric,_ in a["metrics"].items():
        if(metric == "recall" or metric == "precision"):
            if(a["metrics"][metric] < b["metrics"][metric]):
                return False
        elif(a["metrics"][metric] > b["metrics"][metric]):
            return False
    return True
def take_target(elem):
    return elem["target"]


def nn_prune():
    skyline_candidates = candidate_extract("./log/solve_log.json","./log/perform_vectors.log")
    dimension = len(skyline_candidates[0])
    skyline_candidates.sort(key = take_target,reverse=True)
    f_c = open("./log/skyline_candidates.log","w")
    for x in skyline_candidates:
        f_c.write(str(x))
        f_c.write("\n")
    f_c.close()
    skylines=list()
    flag=dict()
    configs = rwjson.json_read("./config/config.json")
    bounds = configs["bounds"]
    for x in skyline_candidates:
        flag[str(x)] = True
        for metric, bound in bounds.items():
            if(metric == "recall" or metric == "precision"):
                if(x["metrics"][metric] < bound):
                    flag[str(x)] = False;
                    break
            else:
                if(x["metrics"][metric] > bound):
                    flag[str(x)] = False;
    cnt=0
    for i in range(0,len(skyline_candidates)-1):
        a = skyline_candidates[i]
        if(not flag[str(a)]):
            continue
        for j in range(i+1,len(skyline_candidates)):
            b = skyline_candidates[j]
            if(not flag[str(b)]):
                continue
            cnt += 1
            if (dominate(a,b)):
                flag[str(b)] = False
            elif (dominate(b,a)):
                flag[str(a)] = False
                break
    f_s = open("./log/skyline_results.log","w")
    ss=[]
    for x in skyline_candidates:
        if(flag[str(x)]):
            f_s.write(str(x))
            f_s.write("\n")
    f_s.close()

def main():
	nn_prune()
	exit()
	candidates = candidate_extract("./log/solve_log.json","./log/perform_vectors.log")
	f_c = open("./log/candidates.log","w")
	for x in candidates:
		f_c.write(str(x))
		f_c.write("\n")
	f_c.close()

if __name__ == "__main__":
	main()

