
import os
import common.utils
from pyinotify import WatchManager, Notifier, ProcessEvent, IN_DELETE, IN_CREATE, IN_MODIFY
import json

#
# 所有监听的客户端，以关注的IP为KEY
# 每一个元素为一个列表
#
Observers = {}

class eventHandler(ProcessEvent):
    def process_IN_MODIFY(self, event):
        fileName = event.name
        if Observers.has_key(fileName):
            clients = Observers[fileName]
            #print "modify file: " + fileName
            if clients:

                # 读取最后一行数据
                line = common.utils.tailFile(event.path +"/"+ fileName,num=2)[1]
                arr = line.split(" ")
                # print "------------------------:" + line
                d = {
                    "ip": event.name,
                    "time": arr[0] + " "+ arr[1],
                    "line": arr[2]
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