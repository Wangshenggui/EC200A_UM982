import usocket



def rtcm_tcp_client(address,port):
    rtcm_sock = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM, usocket.IPPROTO_TCP)   #创建一个 socket 对象
    rtcm_sock.connect((address, port))  #连接到指定的 TCP 服务器
    
    
    request = \
    "GET /"+ "RTCM33_GRCEJ" +" HTTP/1.0\r\n"\
    "User-Agent: NTRIP GNSSInternetRadio/1.4.10\r\n"\
    "Accept: */*\r\n"\
    "Connection: close\r\n"\
    "Authorization: Basic " + "Y2VkcjEzOTIwOmZ5eDYyNzMz" + "\r\n"\
    "\r\n"
    
    rtcm_sock.send(request)
    
    while True:
        try:
            data = rtcm_sock.recv(1024)
            print(data)
        except:
            # Connection ends until the data is fully received
            print('tcp disconnected.')
            rtcm_sock.close()
            break
    
    
    return rtcm_sock

