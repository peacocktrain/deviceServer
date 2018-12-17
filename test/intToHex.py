import binascii

def dealIntStrings(values):
    values = value.split(" ")
    result = ""
    for v in values:
        v = hex(int(v))
        v = v.replace("0x","")
        if len(v) == 1 :
            v = "0" + v
        result = result + "" + v
    print result

def dealHexStrings(values):
    values = value.split(" ")
    result = ""
    for v in values:
        print int(binascii.a2b_hex(v))
        v = hex(binascii.a2b_hex(v))
        v = v.replace("0x","")
        if len(v) == 1 :
            v = "0" + v
        result = result + "" + v
    print result


value = "FE 82 95 00 02 00 00 00 00 01 0B FF 14 00 78 0D 00 00 00 00FF FF 04 00 00 00 00 00 00 00 00 00 D5 03 76 FE C2 00 A6 FD D4 FE FA 00 D5 FD 80 C8 16 BC C4 DE 8B 3C 92 4C BA 3F 00 00 76 00 02 00 5A 00 00 00 02 00 00 00 4C 04 4C 04 4C 04 4C 04 4C 04 4C 04 4C 04 4C 04 98 04 F4 01 FE 01 98 00 F5 01 AB 00 AB 00 F4 01 F4 01 0C 00 47 00 00 00 00 00 00 00 00 00 00 00 34 09 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 23 D6"



# dealHexStrings(value)
print value.replace(" ","")


data = "fe20b3000000030001f171b5602200000000b521003dbbd8063da9114c3d0a0000001500000000000000a35b"
print len(binascii.a2b_hex(data))


