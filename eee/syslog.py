SysLampSignalState = 0    # 存储灯语（lamp signal）信息



# 记录网络错误信息的变量
NetworkErrorMessage_n = 0  # 网络错误编号计数器
NetworkErrorMessage = ""   # 存储网络错误信息的字符串

# 记录网络错误信息的函数
def RecordNetworkError(s):
    global NetworkErrorMessage_n
    global NetworkErrorMessage
    
    # 增加错误编号
    NetworkErrorMessage_n += 1
    
    # 将新的错误信息添加到记录中
    NetworkErrorMessage += "ERROR " + str(NetworkErrorMessage_n) + " :" + s + "\r\n"

# 输出网络错误信息的函数
def GetNetworkErrorMessage():
    global NetworkErrorMessage
    
    # 返回记录的所有网络错误信息
    return NetworkErrorMessage
 # type: ignore