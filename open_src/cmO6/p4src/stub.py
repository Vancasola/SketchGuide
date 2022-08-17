# reconfigure the P4 program
template_file = "p4src/template.p4"
class stub():
	def __init__(self):
		self.stub_hook_param = {1:"hash_cnt",\
			2:"hash_cnt",\
			3:"hash_tbl_size",\
			4:"exact_tbl_size",\
			5:"hash_cnt",\
			6:"reg_size",\
			7:"hash_cnt",\
			8:"hash_cnt",
			}
		self.param_hook_stub = {"hash_cnt":[1,2,5,7,8],\
			"reg_size":[6],\
			"hash_tbl_size":[3],\
			"exact_tbl_size":[4]}
		self.seed=["32w0x30243f0b","32w0x0f79f523","32w0x6b8cb0c5","32w0x00390fc3","32w0x298ac673",\
		  "32w0x04C11DB7","32w0xEDB88320","32w0xDB710641","32w0x82608EDB","32w0x741B8CD7","32w0xEB31D82E"\
		  "32w0xD663B05","32w0xBA0DC66B","32w0x32583499","32w0x992C1A4C","32w0x32583499","32w0x992C1A4C"]#hash_cnt
		self.stub = list()
		self.stub.append(["bit<16> index_j;",\
		 "bit<1> res_j;",\
		 "bit<32> est_j;",\
		 "bit<1> c_j;"])#hash_cnt
		self.stub.append(["ig_md.c_j : exact;"])#hash_cnt
		self.stub.append(["Register<bit<32>, bit<16>>(32wj) flowkey_hash_table;"])#hash_tbl_size
		self.stub.append(["size = j;"])#exact_tbl_size
		self.stub.append(["ig_md.est_j = ig_md.est_j - ig_md.threshold;",\
						  "ig_md.c_j = (bit<1>) ig_md.est_j >> 31;"])#hash_cnt
		self.stub.append(["Register<bit<32>, bit<16>>(32wj) cm_table;"])#reg_size
		self.stub.append(["CM_UPDATE(s) update_j;"])#hash_cnt
		self.stub.append(["update_j.apply(hdr.ipv4.src_addr, ig_md.est_j);"])#hash_cnt

        # hook the P4 primitives with the same parameters
	def hook_code(self, stub_index, param):
		code=""
		if stub_index in self.param_hook_stub["hash_cnt"]:
			for i in range(param):
				for x in self.stub[stub_index-1]:
					if (stub_index == 7):
						code += x.replace("j", str(i+1)).replace("s", self.seed[i]) + "\n"
					else:
						code += x.replace("j", str(i+1)) + "\n"
				code += "\n"
		else:
			x = self.stub[stub_index-1][0]
			code += "    "+x.replace("j", str(param)) + "\n"

		return code

        # replace the stubs with P4 codes
	def replace_stub(self, params):
		f_in=open(template_file,"r")
		text = f_in.read()
		for i in range(len(self.stub)):
			stub_i = "stub_"+str(i+1)
			text = text.replace(stub_i, self.hook_code(i+1, params[self.stub_hook_param[i+1]]))
		f_in.close()
		return text

