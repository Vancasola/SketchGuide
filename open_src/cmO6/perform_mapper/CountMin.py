from perform_mapper import hashes as hashes
import socket,struct
import math
class CountMin():
	def __init__(self, row, col, hash_tbl_size, exact_tbl_size):
		self.row=math.ceil(row)
		self.col=math.ceil(col)
		self.tbl=[]
		for i in range(self.col):
			r=list()
			for j in range(self.row):
				r.append(0)
			self.tbl.append(r)

		self.hashes = hashes.Crc_Hash(col)
		self.hash_tbl = []
		self.hash_tbl_hash = hashes.Crc_Hash(1)
		self.hash_tbl_size = math.ceil(hash_tbl_size)
		for i in range(self.hash_tbl_size):
			self.hash_tbl.append(0)
		self.exact_tbl = []
		self.exact_tbl_size = math.ceil(exact_tbl_size)
	
	def flow_to_bytestream(self,key):
		return socket.inet_aton(key)

	# simulate the exact table
	def update(self, key, val, thresh):
		bit_stream = self.flow_to_bytestream(key)
		for i in range(self.col):
			self.tbl[i][self.hashes[i].bit_by_bit_fast(bit_stream) % self.row] += val

		hash_res = self.hash_tbl_hash[0].bit_by_bit_fast(bit_stream) % self.hash_tbl_size
		if(self.is_heavy_hitter(key,thresh)):
			if(self.hash_tbl[hash_res] == 0):
				self.hash_tbl[hash_res] = key
			elif(key != self.hash_tbl[hash_res] and key not in self.exact_tbl and len(self.exact_tbl)<self.exact_tbl_size):
				self.exact_tbl.append(key)
	
	def estimate(self, key):
		bit_stream = self.flow_to_bytestream(key)
		_min = 1e15
		for i in range(self.col):
			_min = min(_min, self.tbl[i][self.hashes[i].bit_by_bit_fast(bit_stream) % self.row])
		return _min	

	def is_heavy_hitter(self, key, thresh):
		if self.estimate(key)>thresh:
			return True
		return False
	# simulate the hash table
	def detect_heavy_hitter(self, thresh):
		heavy_key_list=list()
		for key in self.exact_tbl:
			heavy_key_list.append(key)
		for key in self.hash_tbl:
			if key != 0:
				heavy_key_list.append(key)
		return heavy_key_list

	def clear(self):
		for i in range(self.col):
			for j in range(self.row):
				self.tbl[i][j] = 0
		for i in range(self.hash_tbl_size):
			self.hash_tbl[i] = 0
		del self.exact_tbl[0:len(self.exact_tbl)]
