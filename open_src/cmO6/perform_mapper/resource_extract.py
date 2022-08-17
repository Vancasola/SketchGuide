def get_resources(f):
	while(True):
		line = f.readline()
		if(line.find("Totals") != -1):
			res = line.split("|")
			break
	resources=dict()
	for i in range(len(res)):
		if(i == 5):
			resources["hash_dist_unit"] = int(res[i])
		elif(i == 7):
			resources["sram"] = int(res[i])
		elif(i == 8):
			resources["map_ram"] = int(res[i])
		elif(i == 11):
			resources["salu"] = int(res[i])
			return resources
def get_stage_cnt(f):
	meet_stage_cnt = 1
	while(True):
		line = f.readline()
		if(meet_stage_cnt == 3):
			for i in range(4):
				line = f.readline()
			break
		if(line.find("Stage") != -1):
				meet_stage_cnt += 1
	stage_cnt=-1
	while(True):
		line = f.readline()
		tmp = line.split("|")
		if(len(tmp)==1):
			return stage_cnt
		if(int(tmp[2])>stage_cnt):
			stage_cnt = int(tmp[2])

def get_resource_usage(log_file):
    f=open(log_file,"r")
    resources=dict()
    resources = get_resources(f)
    resources["stage_count"] = get_stage_cnt(f)
    return resources
