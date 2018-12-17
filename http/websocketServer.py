
from websocket_server import WebsocketServer
import ConfigParser
import json
import threading
import logMonitor

class Device:
    code = ""               # 设备名称
    ip  = ""                # 设备IP
    port = 0                #  在服务端的通信端口
    logPath = ""            # 日志目录
    logFile = None
    encryptionType = ""     # 加密时间
    liveTime = 0            # 连接时间（毫秒）
    missionPlayerClient = {}    # MP连接客户端
    socket = None           # 服务端 Socket 对像
    mpClientNumLimit = {}   # MP客户端连接数量
    logPringCounter = 0

# 初始化配制 , for test
cf = ConfigParser.ConfigParser()
cf.read("../server.conf")
section = "server"
LOG_PATH = cf.get(section,"LOG_PATH")
BIND_IP = cf.get(section,"BIND_IP")
WEBSOCKET_PORT = int(cf.get(section,"WEBSOCKET_PORT"))
DEVICES = {}

# 哪一个用户IP 监听 哪个设备IP
DEVICE_CURRNET_MONITOR_IP = {}

# 当有新设备建立连接时
def deviceConnected(device):
    global DEVICES
    device.ip = "access.log"
    DEVICES[device.ip] = device
    data = { "function": "deviceConnected", "ip": device.ip }
    try:
        server.send_message_to_all(json.dumps(data))
    except:
        pass

# 当有设备断开连接时
def deviceConnectionClose(device):
    global DEVICES
    if( DEVICES.has_key(device.ip) ):
        DEVICES.pop(device.ip)
        data = {"function":"deviceClosed","ip":device.ip}
        try:
            server.send_message_to_all(json.dumps(data))
        except:
            pass

# 新客户端连接时
def newClient(client, server):
    data = {"function":"welcome", "ip":client['address'][0]}
    server.send_message(client, json.dumps(data))

# 客户端断开连接时
def clientClose(client, server):
    clientIP = client['address'][0]
    if DEVICE_CURRNET_MONITOR_IP.has_key(clientIP) :
        deviceIP = DEVICE_CURRNET_MONITOR_IP[clientIP]
        if deviceIP and logMonitor.Observers.has_key(deviceIP):
            clients = logMonitor.Observers[deviceIP]
            for c in clients:
                if c["wsClient"] == client:
                    clients.remove(c)
                    print 'remove ws client: ' + clientIP

# 当接收到消息时
def recvMessage(client, server, msg):

    print "msg  : " + msg
    global LOG_PATH,DEVICES

    # 如果为tail某个机器IP的日志
    if( 0 == msg.find("tail:") ):

        # 把之前监听某个IP的客户端注销
        clientClose( client, server )

        # 把关注的设备IP添加到监听列表对列中
        deviceIP = msg[ msg.find(":")+1: ]

        print "receivei tail: " + deviceIP

        # 哪一个用户 监听 哪个设备
        #       IP   ->   Device
        DEVICE_CURRNET_MONITOR_IP[ client[ 'address'][0] ] = deviceIP
        s = {"wsServer" : server, "wsClient" : client }
        if logMonitor.Observers.has_key(deviceIP):
            logMonitor.Observers[deviceIP].append(s)
        else:
            logMonitor.Observers[deviceIP] = [s]

    # 如果为请求IP列表
    if( 0 == msg.find("getDevices") ):
        data = { 'function':"getDevices",'data': DEVICES.keys() }
        server.send_message(client,json.dumps(data))

server = None
def startWebsocketServer():

    global server
    print "Device Server start at port: ", WEBSOCKET_PORT

    # 初始化WebsocketServer
    server = WebsocketServer(WEBSOCKET_PORT, host=BIND_IP)
    server.set_fn_new_client(newClient)
    server.set_fn_message_received(recvMessage)
    server.set_fn_client_left(clientClose)

    t = threading.Thread(target=server.run_forever)
    t.start()

startWebsocketServer()

d = Device()
d.ip = "access.log"
d.code = "01"
deviceConnected(d)