
import socket
import time
import binascii
import thread
import threading

server_addr = ('jdrone.jd.com', 2002)
# server_addr = ('10.186.130.122',9999)

f = open("fc.txt","r")
hexLines = []
while True:
    l = f.readline().strip()
    if l == "": break
    hexLines.append(l)
threads = []

def start(lines,receiveData = False,group = 100):
    counter = 0
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(server_addr)

    while True:
        for l in lines:
            try:
                client.send(binascii.a2b_hex(l))
                if receiveData :
                    data = client.recv()
            except Exception , e:
                print "error :",e;

        counter += 1
        if 0 != counter and counter % group == 0:
            print threading.currentThread().name," done : ", counter

        time.sleep(.1)


for i in range(0,10):
    t = threading.Thread(name="thread_" + str(i),target=start,args=(hexLines,False,100))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print "Exiting Main Thread"

