
import socket
import time
import binascii

BUF_SIZE = 1024


server_addr = ('111.13.29.155', 2002)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(server_addr)
counter = 0
while True:
    time.sleep(2)
    data = client.send("hahahahaha");
    print data

client.close()