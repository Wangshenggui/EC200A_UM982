# 导入所需的库
import usocket  # 用于网络连接和套接字操作
import _thread  # 用于多线程操作
import utime  # 用于时间管理
import sys  # 用于系统级操作
import ujson  # 用于JSON解析
import sim  # 与SIM卡操作相关的模块

sys.path.append('/usr')  # 将'/usr'路径添加到系统路径
import um982  # 引入um982模块，可能是与硬件或外设相关的操作
import fs  # 文件系统操作模块
import syslog  # 日志记录模块

# 定义一些全局变量
ip = None  # 存储服务器IP地址
port = None  # 存储端口号
mount = None  # 存储挂载点
accpas = None  # 存储认证密码
thread_id = None  # 存储线程ID

# 定义RTC连接的状态
rtcm_sock = None  # 套接字对象
is_connected = 0  # 连接状态（0: 未连接, 1: 连接中, 2: 连接成功, 3: 密码错误）

# 输出调试信息的函数
def printf(s):
    print("[rtcmsocket]: " + s)

# SIM卡状态字典
sim_status_dict = {
    0: "SIM卡不存在/被移除",
    1: "SIM已经准备好",
    2: "SIM卡已锁定，等待CHV1密码",
    3: "SIM卡已被阻拦，需要CHV1密码解锁密码",
    4: "由于SIM/USIM个性化检查失败，SIM卡被锁定",
    5: "由于PCK错误导致SIM卡被阻拦，需要MEP密码解除阻拦",
    6: "需要隐藏电话簿条目的密钥",
    7: "需要解锁隐藏密钥的编码",
    8: "SIM卡已锁定，等待CHV2密码",
    9: "SIM卡被阻拦，需要CHV2解锁密码",
    10: "由于网络个性化检查失败，SIM卡被锁定",
    11: "由于NCK不正确，SIM卡被阻拦，需要MEP解锁密码",
    12: "由于子网络锁个性化检查失败，SIM卡被锁定",
    13: "由于错误的NSCK，SIM卡被阻拦，需要MEP解锁密码",
    14: "由于服务提供商个性化检查失败，SIM卡被锁定",
    15: "由于SPCK错误，SIM卡被阻拦，需要MEP解锁密码",
    16: "由于企业个性化检查失败，SIM卡被锁定",
    17: "由于CCK不正确，SIM卡被阻止，需要MEP解锁密码",
    18: "SIM正在初始化，等待完成",
    19: "CHV1/CHV2/PIN错误",
    20: "SIM卡无效",
    21: "未知状态"
}

# RTCM客户端连接函数
def rtcm_tcp_client():
    global ip, port, mount, accpas
    global rtcm_sock, is_connected, thread_id
    
    # 获取SIM卡状态
    sim_status = sim.getStatus()
    if sim_status not in sim_status_dict:
        printf("接口返回失败")
    if sim_status != 1:
        printf("Get SIM status status : {}".format(sim_status_dict[sim_status]))
        syslog.RecordNetworkError(str.format(sim_status_dict[sim_status]))
    printf("Get sim_status is : {}".format(sim_status_dict[sim_status]))
    
    try:
        # 创建TCP套接字
        rtcm_sock = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
        printf("套接字创建成功")
    except Exception as e:
        printf("创建套接字时出错:", e)
    
    # 设置套接字超时为3秒
    rtcm_sock.settimeout(3)
    
    # 检查配置文件是否存在
    if fs.CreateFile("cors.txt"):
        FileContent = fs.ReadFile("cors.txt")
    else:
        # 配置文件不存在时写入默认配置
        data = {
            "ip": "xxx.xxx.xxx.xxx",
            "port": "65536",
            "mount": "xxxxxxxxxxxx",
            "accpas": "xxxxxxxxxxxxxxxxxxxxxxxx"
        }
        
        # 将字典数据转换为JSON字符串
        json_content = ujson.dumps(data)
        
        # 将JSON内容写入文件
        fs.WriteFile("cors.txt", json_content)
        FileContent = fs.ReadFile("cors.txt")
        
    printf(FileContent)
    
    try:
        # 从文件中提取JSON部分
        json_part = FileContent[FileContent.index('{'):FileContent.index('}') + 1]
        # 解析JSON
        data = ujson.loads(json_part)
        
        # 提取配置信息
        if "ip" in data and "port" in data and "mount" in data and "accpas" in data:
            ip = data["ip"]
            port = data["port"]
            mount = data["mount"]
            accpas = data["accpas"]
    except (ValueError, KeyError) as e:
        print("解析JSON时发生错误:", e)
    
    try:
        # 尝试连接服务器
        rtcm_sock.connect((ip, int(port)))
    except OSError as e:
        printf("连接失败: " + str(e))
        syslog.RecordNetworkError("网络连接失败: " + str(e))
        is_connected = 0
        thread_id = _thread.start_new_thread(RTCM_TCP_thread_temp, ())
        return

    is_connected = 1
    # 准备发送的请求
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
    
    # 启动处理数据的线程
    thread_id = _thread.start_new_thread(RTCM_TCP_thread, ())
    
    utime.sleep_ms(500)
    return rtcm_sock

# 数据处理线程
def RTCM_TCP_thread():
    global is_connected
    global rtcm_sock

    while True:
        if is_connected == 2:  # 判断是否连接成功
            if um982.global_gga_data and len(um982.global_gga_data) > 50:  # 检查GGA数据是否有效
                # 发送GGA数据到服务器
                rtcm_sock.send(um982.global_gga_data + "\r\n")
            else:
                printf("GGA数据为空或长度不够，无法发送")
        
        # 调用接收数据的函数
        rtcm_tcp_read()
        utime.sleep_ms(500)  # 延时以减少CPU占用
        
# 临时线程，用于维持连接
def RTCM_TCP_thread_temp():
    while True:
        utime.sleep_ms(500)  # 延时以减少CPU占用

# 读取和处理服务器返回的数据
def rtcm_tcp_read():
    global is_connected
    global rtcm_sock

    try:
        # 接收数据
        data = rtcm_sock.recv(3276)
        if data:
            utf8_data = data.decode('utf-8')

            # 打印接收到的数据
            if "ICY 200 OK\r\n" in utf8_data:
                is_connected = 2  # 连接成功
                printf(utf8_data)
            elif "ERROR - Bad Password\r\n" in utf8_data:
                is_connected = 3  # 密码错误
                syslog.RecordNetworkError("账号密码错误")
                printf("账号密码错误\r\n")
            else:
                um982.uart_um982.write(data)  # 将数据发送到硬件
    except OSError as e:
        printf("接收数据超时或断开TCP连接: " + str(e))
        syslog.RecordNetworkError("接收数据超时或断开TCP连接: " + str(e))
        return  # 跳出函数
    except Exception as e:
        printf("断开TCP连接: " + str(e))
        syslog.RecordNetworkError("断开TCP连接: " + str(e))
        rtcm_sock.close()  # 关闭套接字
        is_connected = 0  # 设置连接状态为未连接
