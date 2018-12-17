
import logging
import logging.config

logging.config.fileConfig("logging.conf")    # 采用配置文件
logger = logging.getLogger("logfile")


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

if __name__ == "__main__":

    f = open('../server.conf', 'r')  #‘r’的话会有两个\n\n

    print tailFile('../server.conf',2)
    f.close()
    a = ["a","b"]
    a.remove('b')
    print a