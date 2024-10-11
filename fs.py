
# config.ini

um982_configdata = "[um982]\nhello world!\niganma"

def printf(s):
    print("[fs]: " + s)

# def CreateFile(s):
#     path = "/usr/" + s
    
#     try:
#         # 尝试以读写模式打开文件
#         f = open(path, "r+")
#         print("文件已存在，直接打开: {}".format(path))
#         # 写入内容
#         f.write("打开写入: " + path + "\n")  # 写入内容
#     except Exception:  # 捕获所有异常
#         # 文件不存在，创建新文件
#         print("创建新文件: {}".format(path))
#         f = open(path, "w+")
#         filename = s.split('.')[0]  # 获取不带后缀的文件名
#         if filename == "um982":
#             data = um982_configdata
#         else:
#             data = ble_configdata
        
#         # 使用 write() 逐行写入
#         f.write(data)  # 写入每一行
        
#     f.close()  # 关闭文件

def CreateFile(FileName):
    full_path = "/usr/" + FileName
    
    try:
        with open(full_path, "r"):  # 尝试以只读模式打开文件
            printf("文件已存在: {}".format(full_path))
            return True  # 文件已存在
    except Exception:
        # 文件不存在，创建新文件
        printf("创建新文件: {}".format(full_path))
        with open(full_path, "w") as f:
            pass  # 创建空文件并自动关闭
        return False  # 文件已创建

def WriteFile(FileName, s):
    full_path = "/usr/" + FileName
    
    try:
        with open(full_path, "w") as f:
            f.write(s)  # 写入每一行并换行
    except Exception as e:
        printf("写入文件时出错: {}".format(e))

def ReadFile(FileName):
    full_path = "/usr/" + FileName
    
    try:
        with open(full_path, "r") as f:  # 以只读模式打开文件
            content = f.read()  # 读取文件内容
        # printf("文件内容:\n{}".format(content))  # 打印内容
        return content  # 返回读取内容
    except Exception as e:
        printf("读取文件时出错: {}".format(e))  # 捕获并打印异常信息
        return None

        
        
def fs_test():
    CreateFile("fs_test.txt")
    WriteFile("fs_test.txt",um982_configdata)
    ReadFile("fs_test.txt")

