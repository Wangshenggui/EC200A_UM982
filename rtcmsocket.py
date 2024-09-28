import usocket
import _thread
import utime

import sys
sys.path.append('/usr')
import um982

rtcm_sock = None
# 定义全局标志位\
# 0   未连接网络
# 1   已连接网络
# 2   已连接RTCM服务器
# 3   账号密码错误
is_connected = 0

def printf(s):
    print("[rtcmsocket]: " + s)

def rtcm_tcp_client(address,port):
    global rtcm_sock
    global is_connected
    rtcm_sock = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM, usocket.IPPROTO_TCP)   #创建一个 socket 对象
    # rtcm_sock.connect((address, port))  #连接到指定的 TCP 服务器
    try:
        rtcm_sock.connect((address, port))
    except OSError as e:
        printf("连接失败:", e)
        is_connected = 0
        return
    is_connected = 1
    
    request = \
    "GET /"+ "RTCM33_GRCEJ" +" HTTP/1.0\r\n"\
    "User-Agent: NTRIP GNSSInternetRadio/1.4.10\r\n"\
    "Accept: */*\r\n"\
    "Connection: close\r\n"\
    "Authorization: Basic " + "Y2VkcjEzOTIwOmZ5eDYyNzMz" + "\r\n"\
    "\r\n"
    
    # 发送握手消息
    rtcm_sock.send(request)
    
    _thread.start_new_thread(rtcm_tcp_read, (rtcm_sock,))
    
    utime.sleep_ms(500)
    
    return rtcm_sock


def rtcm_tcp_read(socket):
    global is_connected
    while True:
        try:
            data = socket.recv(3276)
            if data:
                utf8_data = data.decode('utf-8')
                
                # 判断是否包含 "ICY 200 OK\r\n"
                if "ICY 200 OK\r\n" in utf8_data:
                    is_connected = 2
                    printf(utf8_data)
                elif "ERROR - Bad Password\r\n" in utf8_data:
                    is_connected = 3
                    printf("账号密码错误\r\n")
                else:
                    um982.uart_um982.write(data)
                    printf("收到差分数据\r\n")
        except:
            printf("断开TCP连接\r\n")
            socket.close()
            break
        
    utime.sleep_ms(10)  # 避免占用过多 CPU
    

