import threading
import binascii
import time

import model.device
#import http.websocketServer

LOG_PATH = ""
BUF_SIZE = 0

timeFormat = '%Y-%m-%d %H:%M:%S'

#
# 新连接请求后，创建此方法的调用线程，子线程进行处理
# parm:
#   client  socket客户端对像
#   closeCallback   回调方法
#
def receiveData( data , device ):

    # 有新设备时 通知客户端
    #http.websocketServer.deviceConnected(device)

    thread = threading.current_thread()
    hex = binascii.b2a_hex( data )
    #print " [" + str( device.logPringCounter ) + "] " + time.strftime(timeFormat) + " " +thread.getName() + ' [' + device.ip + "] " + hex

    # 信息进行文件写入
    device.logFile.write(time.strftime(timeFormat) + " " + hex + "\n")
    device.logFile.flush()

    device.logPringCounter += 1

def closeDevice(device):
    # 客户端关闭后更新当前连接列表
    #http.websocketServer.deviceConnectionClose(device)
    pass

