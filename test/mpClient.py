
import socket
import time
import binascii

BUF_SIZE = 1024
server_addr = ('jdrone.jd.com', 2000)
# server_addr = ('localhost', 9998)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(server_addr)
data = "fe0921000202ff01be000000000006080000035a79"
#data = "fe022b000000ff01beb700002ebb"

while True:
    time.sleep(1)
    client.send(binascii.a2b_hex(data))
    print "mp send data: " ,data

    fcData = client.recv(1024)
    print "mp receive data: " , binascii.b2a_hex(fcData)


print "done"
client.close()