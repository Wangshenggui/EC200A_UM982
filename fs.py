
# config.ini

um982_configdata = \
"[um982]\n\
hello world!\n\
niganma\n"

ble_configdata = \
"[ble]\n\
hello world!\n\
niganma\n"

def CreateFile(s):
    path = "/usr/" + s
    
    try:
        # 尝试以读写模式打开文件
        f = open(path, "r+")
        print("文件已存在，直接打开: {}".format(path))
        # 写入内容
        f.write("打开写入: " + path + "\n")  # 写入内容
    except Exception:  # 捕获所有异常
        # 文件不存在，创建新文件
        print("创建新文件: {}".format(path))
        f = open(path, "w+")
        filename = s.split('.')[0]  # 获取不带后缀的文件名
        if filename == "um982":
            data = um982_configdata
        else:
            data = ble_configdata
        
        # 使用 write() 逐行写入
        f.write(data)  # 写入每一行
        
    f.close()  # 关闭文件
    
    
def ReadFile(filename):
    path = "/usr/" + filename
    
    try:
        with open(path, "r") as f:  # 以只读模式打开文件
            content = f.read()  # 读取文件内容
        print("文件内容:\n{}".format(content))  # 打印内容
    except Exception as e:
        print("读取文件时出错: {}".format(e))  # 捕获并打印异常信息

