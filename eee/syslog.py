# 先不添加这个功能

# 网络错误信息
NetworkErrorMessage_n = 0
NetworkErrorMessage = ""

# 记录网络错误信息
def RecordNetworkError(s):
    global NetworkErrorMessage_n
    global NetworkErrorMessage
    
    NetworkErrorMessage_n += 1
    NetworkErrorMessage +=  "ERROR " + str(NetworkErrorMessage_n) + " :" + s + "\r\n"
    
# 输出网络错误信息
def GetNetworkErrorMessage():
    global NetworkErrorMessage
    
    return NetworkErrorMessage
