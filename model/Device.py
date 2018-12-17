
#
# 设备类，保存设备信息
#


class Device:

    code = None                 # 设备编号，此信息为一个字节，0-255
    ip  = ""                # 设备IP
    port = 0                #  在服务端的通信端口
    logPath = ""            # 日志目录
    logFile = None
    encryptionType = ""     # 加密时间
    liveTime = 0            # 连接时间（毫秒）
    missionPlayerClient = {}    # MP连接客户端
    socket = None           # 服务端 Socket 对像
    mpClientNumLimit = {}   # MP客户端连接数量
    counter = 0


    def __init__(self):
        pass


ds = {}
ds[("a",1) ] = "jory"
ds[("a",2) ] = "jory2"
print ds[('a',2)]