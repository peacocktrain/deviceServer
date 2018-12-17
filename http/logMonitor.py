
import os
from pyinotify import WatchManager, Notifier, ProcessEvent, IN_DELETE, IN_CREATE, IN_MODIFY
import json

# 读取文件最后几行
def tailFile(filePath, num = 1, pos = 0):
    #pos = file.tell()
    file = open(filePath,'r')
    while True:
        pos = pos - 1
        try:
            file.seek(pos, 2)  #从文件末尾开始读
            if file.read(1) == '\n':
                file.seek(file.tell())
                break
        except:     #到达文件第一行，直接读取，退出
            file.seek(0, 0)
            break

    if 0 == num - 1 :
        s =  [file.readline().strip()]
    else:
        s = [file.readline().strip()] + tailFile(filePath,num -1,pos=pos)

    file.close()
    return s


#
# 所有监听的客户端，以关注的IP为KEY
# 每一个元素为一个列表
#
Observers = {}

class eventHandler(ProcessEvent):
    def process_IN_MODIFY(self, event):
        fileName = "access.log"
        print "file change: " + event.path
        if Observers.has_key(fileName):
            clients = Observers[fileName]

            if clients:
                # 读取最后一行数据
                line = tailFile(event.path ,num=2)[1]
                arr = line.split(" ")
                lineDataArr = line.split(arr[1])

                # print "------------------------:" + line
                d = {
                    "ip": "access.log",
                    "time": arr[1],
                    "line": lineDataArr[1]
                }
                data = {"function": "tail", "data": d, "lm":True}

                # 找出感兴趣的客户端列表，并把数据发送出去
                for client in clients:
                    server = client["wsServer"]
                    server.send_message(client["wsClient"], json.dumps(data))
                    #print 'send messge to web client: ' + json.dumps(data)


def fsMonitor(path="/opt/deviceMonitor/access.log"):
    wm = WatchManager()
    mask = IN_DELETE | IN_CREATE | IN_MODIFY
    notifier = Notifier(wm, eventHandler())
    wm.add_watch(path, mask, auto_add= True, rec=True)
    #print "now starting monitor %s." %path

    while True:
        try:
            notifier.process_events()
            if notifier.check_events():
                notifier.read_events()
        except KeyboardInterrupt:
            notifier.stop()
            break

import  threading
t = threading.Thread(target = fsMonitor  )
t.start()