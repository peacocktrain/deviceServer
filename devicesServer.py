
import socket
import threading
import model.device
import ConfigParser

import select
import Queue
import missionPlannerServer
import traceback
import binascii
import logging

from common.utils import logger


PORT = 0                    # 监听端口
BUF_SIZE = 1024             # 读取缓存窗口大小(字节)
BIND_IP = "127.0.0.1"
LOG_PATH = ""
QUEUE_SIZE = 10

# 初始化，从配制文件中初始化变量
def __init__():
    global PORT,BUF_SIZE,BIND_IP,LOG_PATH,QUEUE_SIZE
    cf = ConfigParser.ConfigParser()
    cf.read("server.conf")
    section = "server"
    PORT = int(cf.get(section,"PORT"))
    BIND_IP = cf.get(section, "BIND_IP")
    BUF_SIZE = int(cf.get(section, "BUF_SIZE"))
    LOG_PATH = cf.get(section, "LOG_PATH")
    QUEUE_SIZE = int(cf.get(section,"QUEUE_SIZE"))


__init__()


# 当前子线程列表
threadList = list()

# 开始网络连接
serverAddr = ( BIND_IP, PORT )
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(serverAddr)
server.listen(0)
#server.setblocking(False)

# 可读Socket列表
inputs = [server]
# 可写Socket列表
outputs = []
# 设备地图
deviceConnToHostMap = {}
# 对设备需要写的信息 , 以 IP 为KEY的消息队列
messageForDeviceQueue = {}
# 当前设备列表
DEVIES = {}

# 向飞机发送信息
# deviceCode 设备的ID
def sendMessageToDevice( deviceCode , msg ):

    try:
        global DEVIES, outputs
        d = None
        try:
            # 根据CODE找到对应的device
            for k in DEVIES.keys():
                device = DEVIES[k]
                if device.code == deviceCode:
                    d = device
                    break
        except:
            pass

        # 如果找到在线设备，则下发消息，否则丢掉此信息
        if d and messageForDeviceQueue.has_key((d.ip,d.port)):
            try:
                q = messageForDeviceQueue[(d.ip,d.port)]
                if q.full():
                    q.get_nowait()
                q.put_nowait(msg)
            except:
                pass
            if not d.socket in outputs:
                outputs.append(d.socket)
    except:
        traceback.print_exc()
        pass

# 创建Device对像
def getOrBuildDevice(host, port, socketClient = None):
    global LOG_PATH,DEVIES
    if not DEVIES.has_key((host,port)):
        d = model.device.Device()
        d.ip = host
        d.port = port
        d.logPath = LOG_PATH + '' + d.ip
        d.logFile = open(LOG_PATH + d.ip ,'a')
        d.code = "-1"
        DEVIES[(host,port)] = d
    else:
        d = DEVIES[(host,port)]

    if socketClient:
        d.socket = socketClient
    return d


def closeConnection(host, port, s):
    global DEVIES
    if DEVIES.has_key((host,port)):
        del DEVIES[(host,port)]
    if messageForDeviceQueue.has_key((host,port)):
        messageForDeviceQueue.pop((host,port))
    if s in outputs:
        outputs.remove(s)
    inputs.remove(s)
    s.close()


def deviceServer():
    global messageForDeviceQueue, outputs,logger

    logger.info( "Device Server start at port:  " + str(PORT) )

    # TCP 入口主程序，负责接收网络连接，然后分发到子线程处理
    while True:
        try:
            #global  PORT
            readables, writables, exceptional = select.select(inputs, outputs, [],.5 )
        except:
            if not (readables or writables or exceptional):
                break
        else:

            # 循环处理 可读 列表
            for s in readables:
                if s is server:
                    # 接收网络请求
                    connection, addr = s.accept()
                    connection.setblocking(0)
                    logger.info( "Device connection from: " + addr[0] + ":" + str(addr[1]) )
                    inputs.append(connection)
                    deviceConnToHostMap[connection] = addr
                    messageForDeviceQueue[(addr[0],addr[1])] = Queue.Queue(QUEUE_SIZE)
                    getOrBuildDevice(addr[0], addr[1], connection)

                # 如果是客户端其它数据进来
                else:
                    host, port = deviceConnToHostMap[s]
                    try:
                        data = s.recv(BUF_SIZE)
                    except socket.error, e:
                        if 10035 == e.errno:
                            continue
                        # 如果对方强制关闭
                        else:
                            logger.info( "closing FC:" + host )
                            closeConnection(host,port,s)
                    except:
                        continue
                    else:
                        # 0000000000000000000000000000000000000000000000000000000000000000
                        host, port = deviceConnToHostMap[s]
                        # 如果读数据成功，则处理由客户端上传数据
                        if data:
                            d = getOrBuildDevice(host, port, s)
                            d.counter += 1
                            hexData = binascii.b2a_hex(data)

                            # 如果上传数据大于，则取第四个字节做为设备编号
                            if "-1" == d.code and len(data) > 4 and "fe" == hexData[0:2] :
                                d.code = hexData[6:8]
                                logger.debug("get the FC code:" + d.code + "  msg:" + hexData)

                            # 处理设备上传的数据
                            # service.logServerService.receiveData(data, d)
                            # 信息透传到 MissionPlanner
                            missionPlannerServer.sendMessageToMPClient(data,d)
                            logger.debug("data from FC " + host + " " + hexData )

                            # if s not in outputs:
                            #     outputs.append(s)

                        # 如果为客户端关闭请求
                        else:
                            closeConnection(host, port, s)

            # 循环处理 可写 处理列表
            for s in writables:
                host, port = deviceConnToHostMap[s]
                try:
                    # 如果有消息放在此连接的消息队列中，则进行下发
                    msg = messageForDeviceQueue[(host,port)].get_nowait()
                except Exception,e:
                    if s in outputs:
                        outputs.remove(s)
                    pass
                else:
                    # 111111111111111111111111111111111111111111111111111111111111111111111111
                    logger.debug( "sending to FC " + host + " " + binascii.b2a_hex(msg) )
                    try:
                        s.sendall(msg)
                    except:
                        if s in outputs:
                            outputs.remove(s)
                        logger.error( "sending to FC FAILED "  + host + ":"  + str(port) + " : "+ binascii.b2a_hex(msg) )
                        pass


            for s in exceptional:
                logger.error( " exception condition on " + s.getpeername() )
                if s in outputs:
                    outputs.remove(s)
                inputs.remove(s)
                s.close()

