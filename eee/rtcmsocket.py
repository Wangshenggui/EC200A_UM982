import usocket
import _thread
import utime
import sys
import ujson
import sim

sys.path.append('/usr')
import um982
import fs
import syslog

ip = None
port = None
mount = None
accpas = None
thread_id = None


# 定义全局变量
rtcm_sock = None
is_connected = 0  # 0: 未连接, 1: 连接中, 2: 连接成功, 3: 密码错误

def printf(s):
    print("[rtcmsocket]: " + s)

sim_status_dict={
    0:"SIM卡不存在/被移除",
    1:"SIM已经准备好",
    2:"SIM卡已锁定，等待CHV1密码",
    3:"SIM卡已被阻拦，需要CHV1密码解锁密码",
    4:"由于SIM/USIM个性化检查失败，SIM卡被锁定",
    5:"由于PCK错误导致SIM卡被阻拦，需要MEP密码解除阻拦",
    6:"需要隐藏电话簿条目的密钥",
    7:"需要解锁隐藏密钥的编码",
    8:"SIM卡已锁定，等待CHV2密码",
    9:"SIM卡被阻拦，需要CHV2解锁密码",
    10:"由于网络个性化检查失败，SIM卡被锁定",
    11:"由于NCK不正确，SIM卡被阻拦，需要MEP解锁密码",
    12:"由于子网络锁个性化检查失败，SIM卡被锁定",
    13:"由于错误的NSCK，SIM卡被阻拦，需要MEP解锁密码",
    14:"由于服务提供商个性化检查失败，SIM卡被锁定",
    15:"由于SPCK错误，SIM卡被阻拦，需要MEP解锁密码",
    16:"由于企业个性化检查失败，SIM卡被锁定",
    17:"由于CCK不正确，SIM卡被阻止，需要MEP解锁密码",
    18:"SIM正在初始化，等待完成",
    19:"CHV1/CHV2/PIN错误",
    20:"SIM卡无效",
    21:"未知状态"
}

def rtcm_tcp_client():
    global ip
    global port
    global mount
    global accpas
    
    global rtcm_sock
    global is_connected
    
    global thread_id
    
    sim_status = sim.getStatus()
    if sim_status not in sim_status_dict:
        printf("接口返回失败")
    if sim_status != 1:
        printf("Get SIM status status : {}".format(sim_status_dict[sim_status]))
        syslog.RecordNetworkError(str.format(sim_status_dict[sim_status]))
    printf("Get sim_status is : {}".format(sim_status_dict[sim_status]))
    
    
    try:
        rtcm_sock = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
        printf("套接字创建成功")
    except Exception as e:
        printf("创建套接字时出错:", e)
    
    # 设置超时为3秒
    rtcm_sock.settimeout(3)
    
    # 检查文件是否存在
    if fs.CreateFile("cors.txt"):
        FileContent = fs.ReadFile("cors.txt")
    else:
        # 写入数据到文件(默认没有CORS账号信息，需要通过蓝牙进行配置)
        data = {
            "ip":"xxx.xxx.xxx.xxx",
            "port":"65536",
            "mount":"xxxxxxxxxxxx",
            "accpas":"xxxxxxxxxxxxxxxxxxxxxxxx"
        }
        
        # 将字典数据转换为JSON字符串
        json_content = ujson.dumps(data)
        
        # 写入JSON内容到文件
        fs.WriteFile("cors.txt", json_content)
        FileContent = fs.ReadFile("cors.txt")
        
    printf(FileContent)
    
    try:
        # 提取JSON部分
        json_part = FileContent[FileContent.index('{'):FileContent.index('}') + 1]
        # 解析JSON
        data = ujson.loads(json_part)
        
        # 检查键是否存在
        if "ip" in data and "port" in data and "mount" in data and "accpas" in data:
            ip = data["ip"]
            port = data["port"]
            mount = data["mount"]
            accpas = data["accpas"]
    except (ValueError, KeyError) as e:
        print("解析JSON时发生错误:", e)
    
    try:
        rtcm_sock.connect((ip,int(port)))
    except OSError as e:
        printf("连接失败: " + str(e))
        syslog.RecordNetworkError("网络连接失败: " + str(e))
        is_connected = 0
        return

    is_connected = 1
    request = (
        "GET /" + mount + " HTTP/1.0\r\n"
        "User-Agent: NTRIP GNSSInternetRadio/1.4.10\r\n"
        "Accept: */*\r\n"
        "Connection: close\r\n"
        "Authorization: Basic " + accpas + "\r\n"
        "\r\n"
    )
    
    # 发送握手消息
    rtcm_sock.send(request.encode())
    
    thread_id = _thread.start_new_thread(RTCM_TCP_thread, ())
    
    utime.sleep_ms(500)
    return rtcm_sock

def RTCM_TCP_thread():
    global is_connected
    global rtcm_sock

    while True:
        if is_connected == 2:  # 判断TCP是否连接
            if um982.global_gga_data and len(um982.global_gga_data) > 50:  # 检查数据是否为空且长度大于50
                # printf("发送GGA到服务器")
                rtcm_sock.send(um982.global_gga_data + "\r\n")
            else:
                printf("GGA数据为空或长度不够，无法发送")
        
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
            # printf("收到数据字节数: " + str(len(data)) + " 字节")
            
            if "ICY 200 OK\r\n" in utf8_data:
                is_connected = 2
                printf(utf8_data)
            elif "ERROR - Bad Password\r\n" in utf8_data:
                is_connected = 3
                syslog.RecordNetworkError("账号密码错误")
                printf("账号密码错误\r\n")
            else:
                um982.uart_um982.write(data)
                # printf("收到差分数据\r\n")
    except OSError as e:
        printf("接收数据超时或断开TCP连接: " + str(e))
        syslog.RecordNetworkError("接收数据超时或断开TCP连接: " + str(e))
        return  # 跳出函数
    except Exception as e:
        printf("断开TCP连接: " + str(e))
        syslog.RecordNetworkError("断开TCP连接: " + str(e))
        rtcm_sock.close()
        is_connected = 0


