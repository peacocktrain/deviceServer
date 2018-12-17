import socket
import time
import binascii

mpData = "fe0921000202ff01be000000000006080000035a79"
fcData = "FE8295000202010000010BFF1400780D00000000FFFF04000000000000000000D50376FEC200A6FDD4FEFA00D5FD80C816BCC4DE8B3C924CBA3F0000760002005A000000020000004C044C044C044C044C044C044C044C049804F401FE019800F501AB00AB00F401F4010C00470000000000000000000000340900000000000000000000000000000000000023D6"

def test_multi(buf, offset = 0):
    return buf[offset] + 0  + 0x0000 + 0x000000 + 0x00000000

def getInt2FromHex(data,offset):
    offset = offset * 2
    value = data[offset] + data[offset+1]
    return int(value,16)

print "MP:"
print  "len:   ", getInt2FromHex(mpData,1)
print  "area:  ", getInt2FromHex(mpData,3)
print  "state: ", getInt2FromHex(mpData,4)
print  "manu:  ", getInt2FromHex(mpData,5)
print  "src:   ", getInt2FromHex(mpData,6)
print  "desc:  ",getInt2FromHex(mpData,7)
print  "msgid: ",getInt2FromHex(mpData,9)

print '-----------------------------------------------------'
print "FC:"
print  "len:   ", getInt2FromHex(fcData,1)
print  "area:  ", getInt2FromHex(fcData,3)
print  "state: ", getInt2FromHex(fcData,4)
print  "manu:  ", getInt2FromHex(fcData,5)
print  "src:   ", getInt2FromHex(fcData,6)
print  "desc:  ",getInt2FromHex(fcData,7)
print  "msgid: ",getInt2FromHex(fcData,9)






