import usocket
import _thread
import utime

import sys
sys.path.append('/usr')
import um982

rtcm_sock = None

def rtcm_tcp_client(address,port):
    global rtcm_sock
    rtcm_sock = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM, usocket.IPPROTO_TCP)   #创建一个 socket 对象
    rtcm_sock.connect((address, port))  #连接到指定的 TCP 服务器
    
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
    while True:
        try:
            data = socket.recv(3276)
            if data:
                utf8_data = data.decode('utf-8')
                print(utf8_data)
                um982.uart_um982.write(data)
        except:
            print("断开TCP连接\r\n")
            socket.close()
            break
        
    utime.sleep_ms(10)  # 避免占用过多 CPU
    

