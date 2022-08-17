import json
def json_read(filename):
	manifest=open(filename,"r")
	data=json.load(manifest)
	manifest.close()
	return data

def json_write(filename,data):
	data_json=json.dumps(data,indent=4,separators=(',', ': '))
	manifest=open(filename,"w")
	manifest.write(data_json)
	manifest.close()