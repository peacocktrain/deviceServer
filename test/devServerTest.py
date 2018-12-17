
import socket
import threading

import time
import binascii
import model.device
import ConfigParser

PORT = 0                    # 监听端口
BUF_SIZE = 1024             # 读取缓存窗口大小(字节)
BIND_IP = "127.0.0.1"
LOG_PATH = ""

LOG_PATH = ""
BUF_SIZE = 0

timeFormat = '%Y-%m-%d %H:%M:%S'

# 初始化，从配制文件中初始化变量
def __init__():
    global PORT,BUF_SIZE,BIND_IP,LOG_PATH
    cf = ConfigParser.ConfigParser()
    cf.read("server.conf")
    section = "server"
    PORT = int(cf.get(section,"PORT"))
    BIND_IP = cf.get(section, "BIND_IP")
    BUF_SIZE = int(cf.get(section, "BUF_SIZE"))
    LOG_PATH = cf.get(section, "LOG_PATH")
    service.serverService.BUF_SIZE = BUF_SIZE

__init__()

# 当前接入的设备列表，以IP为KEY保存 Device 实例
http.websocketServer.DEVICES = {}

# 当前子线程列表
threadList = list()

# 开始网络连接
serverAddr = ( BIND_IP, PORT )
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(serverAddr)
server.listen(5)



def acceptWorker( client, device, closeCallback = None ):

    global  BUF_SIZE
    thread = threading.current_thread()
    print time.strftime(timeFormat) + " accept device in " + thread.getName() + " -- " + device.ip + ":" + str(device.port)
    f = open(device.logPath,"a")
    num = 0

    while True:
        try:
            data = client.recv( BUF_SIZE )
            if not data:
                break
            hex = binascii.b2a_hex( data )
            print " [" + str(num) + "] " + time.strftime(timeFormat) + " " +thread.getName() + ' [' + device.ip + "] " + hex
            f.write(time.strftime(timeFormat) + " " + hex + "\n")
            f.flush()
            # 不回发数据
            #client.sendall( data )
            num += 1
        except:
            break

    print time.strftime(timeFormat) + " device disconnect in ", thread.getName() , "--", device.ip + ":" + str(device.port)
    client.close()

    # 客户端关闭后更新当前连接列表
    http.websocketServer.deviceConnectionClose(device)

    exit(0)




#
# TCP 入口主程序，负责接收网络连接，然后分发到子线程处理
#
while True:

    try:
        client, clientAddr = server.accept()
    except:
        exit(0)

    d = model.device.Device()
    d.ip = clientAddr[0]
    d.port = clientAddr[1]
    d.socket = client
    d.logPath = LOG_PATH+''+d.ip


    http.websocketServer.DEVICES[d.ip] = d

    # 接入连接后，启动新线程处理请求
    t = threading.Thread(target = service.serverService.acceptWorker, args = (client, d))
    t.start()


server.close()

