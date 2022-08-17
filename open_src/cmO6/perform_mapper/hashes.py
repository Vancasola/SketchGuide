import hashlib
from perform_mapper.crc import Crc

crc32_polinomials = [0x30243f0b,0x0f79f523,0x6b8cb0c5,0x00390fc3,0x298ac673,
                     0x04C11DB7, 0xEDB88320, 0xDB710641, 0x82608EDB, 0x741B8CD7, 0xEB31D82E,
                     0xD663B05, 0xBA0DC66B, 0x32583499, 0x992C1A4C, 0x32583499, 0x992C1A4C]

def Crc_Hash(register_num):
    hashes = []
    for i in range(register_num):
        hashes.append(Crc(32, crc32_polinomials[i], True, 0xffffffff, True, 0xffffffff))
    return hashes

