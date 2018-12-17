import threading
import binascii
import time
import http.websocketServer

LOG_PATH = ""
BUF_SIZE = 0

timeFormat = '%Y-%m-%d %H:%M:%S'

#
# 新连接请求后，创建此方法的调用线程，子线程进行处理
# parm:
#   client  socket客户端对像
#   closeCallback   回调方法
#
def acceptWorker( client, device, closeCallback = None ):
    global  BUF_SIZE
    thread = threading.current_thread()
    #print time.strftime(timeFormat) + " accept device in " + thread.getName() + " -- " + device.ip + ":" + str(device.port)
    f = open(device.logPath,"a")
    num = 0

    # 有新设备时 通知客户端
    http.websocketServer.deviceConnected(device)

    while True:
        try:
            data = client.recv( BUF_SIZE )
            if not data:
                break
            hex = binascii.b2a_hex( data )
            # print " [" + str(num) + "] " + time.strftime(timeFormat) + " " +thread.getName() + ' [' + device.ip + "] " + hex
            f.write(time.strftime(timeFormat) + " " + hex + "\n")
            f.flush()
            # 不回发数据
            #client.sendall( data )
            num += 1
        except:
            break
    #print time.strftime(timeFormat) + " device disconnect in ", thread.getName() , "--", device.ip + ":" + str(device.port)
    client.close()

    # 客户端关闭后更新当前连接列表
    http.websocketServer.deviceConnectionClose(device)

    exit(0)
