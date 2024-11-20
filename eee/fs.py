# config.ini

# 配置数据示例
um982_configdata = "[um982]\nhello world!\niganma"

# 打印文件系统操作的信息
def printf(s):
    print("[fs]: " + s)

# 创建文件函数
def CreateFile(FileName):
    full_path = "/usr/" + FileName  # 获取文件的完整路径
    
    try:
        with open(full_path, "r"):  # 尝试以只读模式打开文件
            printf("文件已存在: {}".format(full_path))  # 如果文件已存在，打印消息
            return True  # 文件已存在，返回True
    except Exception:
        # 文件不存在，创建新文件
        printf("创建新文件: {}".format(full_path))  # 打印创建新文件的消息
        with open(full_path, "w") as f:
            pass  # 创建空文件并自动关闭
        return False  # 返回False，表示文件已创建

# 写入文件内容的函数
def WriteFile(FileName, s):
    full_path = "/usr/" + FileName  # 获取文件的完整路径
    
    try:
        with open(full_path, "w") as f:  # 以写模式打开文件
            f.write(s)  # 写入指定的内容
    except Exception as e:
        printf("写入文件时出错: {}".format(e))  # 捕获并打印写入文件时的错误

# 读取文件内容的函数
def ReadFile(FileName):
    full_path = "/usr/" + FileName  # 获取文件的完整路径
    
    try:
        with open(full_path, "r") as f:  # 以只读模式打开文件
            content = f.read()  # 读取文件内容
        return content  # 返回读取到的文件内容
    except Exception as e:
        printf("读取文件时出错: {}".format(e))  # 捕获并打印读取文件时的错误
        return None  # 如果发生异常，返回None

# 文件系统测试函数
def fs_test():
    CreateFile("fs_test.txt")  # 创建名为 fs_test.txt 的文件
    WriteFile("fs_test.txt", um982_configdata)  # 写入配置数据
    ReadFile("fs_test.txt")  # 读取并返回文件内容
