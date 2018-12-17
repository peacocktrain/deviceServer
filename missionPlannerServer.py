
import socket
import threading
import model.device
import ConfigParser
import select
import Queue
import  devicesServer
import traceback
import binascii
from common.utils import logger

MP_PORT = 0                    # 监听端口
BUF_SIZE = 1024             # 读取缓存窗口大小(字节)
BIND_IP = "127.0.0.1"
LOG_PATH = ""
QUEUE_SIZE = 10

# 地面站
MISSION_PLANNER_S = {}

# 初始化，从配制文件中初始化变量
def __init__():
    global MP_PORT,BUF_SIZE,BIND_IP,LOG_PATH,QUEUE_SIZE
    cf = ConfigParser.ConfigParser()
    cf.read("server.conf")
    section = "server"
    MP_PORT = int(cf.get(section, "PM_PORT"))
    BIND_IP = cf.get(section, "BIND_IP")
    BUF_SIZE = int(cf.get(section, "BUF_SIZE"))
    LOG_PATH = cf.get(section, "LOG_PATH")
    QUEUE_SIZE = int(cf.get(section,"QUEUE_SIZE"))
__init__()

# 当前子线程列表
threadList = list()

# 开始网络连接
serverAddr = (BIND_IP, MP_PORT)
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
deviceConnectionToIPMap = {}
# 对设备需要写的信息 , 以 IP 为KEY的消息队列
messageForMPQueue = {}

# 创建Device对像
def getOrBuildMPClient( host, port, socketClient = None  ):
    global LOG_PATH,MISSION_PLANNER_S
    if not MISSION_PLANNER_S.has_key( (host,port) ):
        d = model.device.Device()
        d.ip = host
        d.port = port
        d.logPath = LOG_PATH + '' + d.ip
        #d.logFile = open(LOG_PATH + d.ip +"_mp",'a')
        MISSION_PLANNER_S[ (host, port) ] = d
    else:
        d = MISSION_PLANNER_S[ (host, port ) ]
    if socketClient:
        d.socket = socketClient  # Socket连接语句柄
    return d;

# 发送信息到
def sendMessageToMPClient(msg, device):
    global deviceConnectionToIPMap,outputs,messageForMPQueue
    for conn in deviceConnectionToIPMap.keys():
        addr = deviceConnectionToIPMap[conn]
        d = getOrBuildMPClient( addr[0], addr[1] )
        if d.code:
            try:
                # 只发给对应用的MP
                if device.code != d.code: continue
                q = messageForMPQueue[d]
                #如果满了，则弹出一个
                if q.full():
                    q.get_nowait()
                q.put_nowait(msg)
                if not conn in outputs:
                    outputs.append(conn)
                    logger.debug("MP outputs conn: " + str(len(outputs)))
            except:
                traceback.print_exc()
                logger.error("add MP msg QUEUE ERROR :" + binascii.b2a_hex(msg ))
                pass

# 断开网络连接
def closeConnect(host, port, s):
    global messageForMPQueue
    logger.debug( "closing MP: " + host + " : " + str(port) )
    if s in outputs:
        outputs.remove(s)
    d = getOrBuildMPClient(host, port )
    if messageForMPQueue.has_key(d):
        q = messageForMPQueue[d]
        messageForMPQueue.pop(d)
    del deviceConnectionToIPMap[s]
    inputs.remove(s)
    s.close()



def missionPlannerServer():

    global inputs,outputs,MISSION_PLANNER_S,deviceConnectionToIPMap,messageForMPQueue,logger
    logger.info("Mission Planner Server start at port:  " + str(MP_PORT) )

    # TCP 入口主程序，负责接收网络连接，然后分发到子线程处理
    while True:
        # global MP_PORT
        try:
            readables, writables, exceptional = select.select( inputs, outputs, [], .5)
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
                    logger.info( "MP connection from: " + addr[0] + ":" + str(addr[1]) )
                    inputs.append(connection)
                    # 接受客户端连接请求
                    deviceConnectionToIPMap[connection] = addr
                    d = getOrBuildMPClient(addr[0], addr[1], connection)
                    messageForMPQueue[d] = Queue.Queue(QUEUE_SIZE)

                # 如果是客户端上传数据进来
                else:
                    host, port = deviceConnectionToIPMap[s]
                    if deviceConnectionToIPMap.has_key(s):
                        try:
                            data = s.recv(BUF_SIZE)
                        except socket.error, e:
                            if 10035 == e.errno:
                                continue
                            # 如果对方强制关闭
                            else:
                                closeConnect(host,port,s)
                        except:
                            continue
                        else:
                            # 如果读数据成功，则处理由客户端上传数据
                            if data:
                                hexData = binascii.b2a_hex(data)
                                logger.debug( "data from MP " + host + ":"+ str(port) + " " + hexData )

                                # 获取连接设备
                                d = getOrBuildMPClient(addr[0], addr[1], s)
                                d.counter += 1

                                # 第一次连接，第一个上行数据包为两个字节时
                                # 第一个字节，为指令，00则认为是关注哪个FC (此版忽略)
                                # 第二个字节，为数据，当第一个字节为00时，则代码关注哪个设备
                                if 5 > d.counter and len(data) == 2 :
                                    d.code = hexData[2:4]
                                else:
                                    devicesServer.sendMessageToDevice(d.code, data)

                                    # 处理客户端上传的数据
                                # if s not in outputs:
                                #     outputs.append(s)

                            # 如果为客户端关闭请求
                            else:
                                closeConnect(host,port,s)
                                pass

            # 循环处理 可写 处理列表
            for s in writables:
                host, port = deviceConnectionToIPMap[s]

                try:
                    d = getOrBuildMPClient( host, port, s )
                    # 如果有消息放在此连接的消息队列中，则进行下发
                    msg = messageForMPQueue[d].get_nowait()
                # 如果队列为空
                except Exception,e:
                    if s in outputs:
                        outputs.remove(s)
                else:
                    try:
                        logger.debug( "sending to MP "  + host + ":"  + str(port) + " "+ binascii.b2a_hex(msg) )
                        s.sendall(msg)
                        #messageForMPQueue[d].task_done()
                    except:
                        logger.error( "sending to MP FAILED "  + host + ":"  + str(port) + " "+ binascii.b2a_hex(msg) )
                        pass

            for s in exceptional:
                logger.error( " exception condition on "+ s.getpeername() )
                if s in outputs:
                    outputs.remove(s)
                inputs.remove(s)
                s.close()

    print "mp server done!!!!!!!!"
