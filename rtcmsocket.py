import usocket
import _thread
import utime
import sys

sys.path.append('/usr')
import um982
import fs

# 定义全局变量
rtcm_sock = None
is_connected = 0  # 0: 未连接, 1: 连接中, 2: 连接成功, 3: 密码错误

def printf(s):
    print("[rtcmsocket]: " + s)

def rtcm_tcp_client():
    global rtcm_sock
    global is_connected

    rtcm_sock = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
    
    # 设置超时为3秒
    rtcm_sock.settimeout(3)
    
    if fs.CreateFile("cors.txt") == True:
        FileContent = fs.ReadFile("cors.txt")
    else:
        fs.WriteFile("cors.txt",("120.253.226.97\r\n"
                                 "8002\r\n"
                                 "RTCM33_GRCEJ\r\n"
                                 "Y2VkcjEzOTIwOmZ5eDYyNzMz"))
        FileContent = fs.ReadFile("cors.txt")
        
    printf(FileContent)
    
    
    try:
        rtcm_sock.connect(("120.253.226.97",8002))
    except OSError as e:
        printf("连接失败: " + str(e))
        is_connected = 0
        return

    is_connected = 1
    request = (
        "GET /RTCM33_GRCEJ HTTP/1.0\r\n"
        "User-Agent: NTRIP GNSSInternetRadio/1.4.10\r\n"
        "Accept: */*\r\n"
        "Connection: close\r\n"
        "Authorization: Basic Y2VkcjEzOTIwOmZ5eDYyNzMz\r\n"
        "\r\n"
    )
    
    # 发送握手消息
    rtcm_sock.send(request.encode())
    
    _thread.start_new_thread(RTCM_TCP_thread, ())
    
    utime.sleep_ms(500)
    return rtcm_sock

def RTCM_TCP_thread():
    global is_connected
    global rtcm_sock

    while True:
        if is_connected == 2:  # 判断TCP是否连接
            if um982.global_gga_data and len(um982.global_gga_data) > 50:  # 检查数据是否为空且长度大于50
                printf("发送GGA到服务器")
                rtcm_sock.send(um982.global_gga_data + "\r\n")
            else:
                printf("GGA数据为空或长度不够，无法发送")
        else:
            printf("未连接RTCM服务器")
        
        rtcm_tcp_read()
        utime.sleep_ms(500)  # 避免占用过多 CPU


def rtcm_tcp_read():
    global is_connected
    global rtcm_sock

    try:
        data = rtcm_sock.recv(3276)
        if data:
            utf8_data = data.decode('utf-8')

            # 打印接收到的字节数
            printf("收到数据字节数: " + str(len(data)) + " 字节")
            
            if "ICY 200 OK\r\n" in utf8_data:
                is_connected = 2
                printf(utf8_data)
            elif "ERROR - Bad Password\r\n" in utf8_data:
                is_connected = 3
                printf("账号密码错误\r\n")
            else:
                um982.uart_um982.write(data)
                printf("收到差分数据\r\n")
    except OSError as e:
        printf("接收数据超时或断开TCP连接: " + str(e))
        return  # 跳出函数
    except Exception as e:
        printf("断开TCP连接: " + str(e))
        rtcm_sock.close()
        is_connected = 0


