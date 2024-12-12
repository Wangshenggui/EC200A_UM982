import utime # type: ignore
import _thread
import ujson # type: ignore
from misc import Power # type: ignore
import voiceCall # type: ignore

import sys
# 添加 /usr 目录到模块搜索路径
sys.path.append('/usr')
import um982
import ble
import fs
import rtcmsocket
import appfota
import usruart

# 调试
DEBUG = True

# 创建信号量用于控制线程同步
at_semaphore = _thread.allocate_semphore(1)
thread_id = None

# 标记是否停止
stop = True

# 打印信息函数
def printf(s):
    if DEBUG:
        print("[ble_at]: " + s)


# 初始化AT线程
def init_at():
    global thread_id
    # 启动AT线程
    thread_id = _thread.start_new_thread(AT_thread, ())


# 计算字符串的异或值并返回带有校验码的格式化字符串
def xor_string(s):
    result = 0
    for char in s:
        result ^= ord(char)  # 对字符的ASCII值进行异或
    hex_result = "{:02x}".format(result).upper()  # 转为16进制
    return s + "*" + hex_result + "\r\n"  # 返回带有校验码的字符串


# 创建一个锁对象用于线程安全的资源访问
lock = _thread.allocate_lock()

# 定义回调函数来处理模块的回调事件
def event_callback(event_args):
    """
    处理 voiceCall 模块的回调事件。
    :param event_args: tuple，回调事件参数
    """
    # 解构回调参数
    event_type, call_id, reason_code, state_code, reserved1, reserved2, phone_number, number_type, extra_info = event_args

    # 打印回调信息
    printf("收到回调事件: {0}".format(event_args))
    
    # 根据事件类型处理逻辑
    if event_type == 14:  # 呼出中
        printf("正在拨打电话：{0}...".format(phone_number))
    elif event_type == 11:  # 电话已接通
        printf("电话已接通：{0}。".format(phone_number))
    elif event_type == 12:  # 电话已挂断
        printf("电话已挂断：{0}。".format(phone_number))
        rtcmsocket.rtcm_sock.close()
        _thread.stop_thread(rtcmsocket.thread_id)
        rtcmsocket.rtcm_tcp_client()
    else:
        printf("未知事件类型：{0}".format(event_type))

# 注册回调函数（假设模块需要手动注册回调）
voiceCall.setCallback(event_callback)
        
# AT指令处理的主线程
def AT_thread():
    global stop
    while True:
        # 获取信号量
        at_semaphore.acquire()

        printf("信号量" + ble.at_message + str(ble.at_message_flat))

        # 处理蓝牙串口的AT命令
        if ble.at_message_flat == 1:
            if "AT\r\n" in ble.at_message:
                # 如果是AT命令，返回OK
                ble.ble_send_string("OK\r\n")
            elif "AT+Call=" in ble.at_message:
                # 处理打电话命令
                with lock:
                    start_index = ble.at_message.index('=') + 1
                    end_index = ble.at_message.index('\r\n', start_index)
                    instruct = ble.at_message[start_index:end_index]
                    
                    # um982.uart_um982.write(instruct + "\r\n")
                    printf(instruct)
                    
                    voiceCall.callEnd()
                    voiceCall.callEnd()
                    voiceCall.callEnd()
                    result = voiceCall.callStart(instruct)    # 打电话
                    if result == 0:
                        printf("电话拨打成功，正在呼出...")
                    else:
                        printf("电话拨打失败，错误码：{0}".format(result))
            elif "AT+Name=" in ble.at_message:
                # 处理设置蓝牙名称的命令
                start_index = ble.at_message.index('=') + 1
                end_index = ble.at_message.index('\r\n', start_index)
                name = ble.at_message[start_index:end_index]
                printf("Extracted name: " + name)
                # 发送设置蓝牙名称的命令
                ble.uart_ble.write("AT+QBLENAME=" + name + "\r\n")
                ble.ble_send_string("OK\r\n")
                # ble.ble_send_string("OK\r\n")
                # ble.ble_send_string("OK\r\n")
            elif "AT+{" in ble.at_message:
                try:
                    # 处理带有JSON数据的AT命令
                    json_part = ble.at_message[ble.at_message.index('{'):ble.at_message.index('}') + 1]
                    data = ujson.loads(json_part)

                    # 检查关键字段是否存在
                    if "ip" in data and "port" in data and "mount" in data and "accpas" in data:
                        # 将配置写入文件并打印
                        fs.WriteFile("cors.txt", json_part)
                        FileContent = fs.ReadFile("cors.txt")
                        printf(FileContent)
                        printf("系统即将重启...")
                        ble.ble_send_string("系统即将重启...")
                        ble.ble_send_string("OK\r\n")
                        # utime.sleep_ms(10)
                        # ble.ble_send_string("OK\r\n")
                        # utime.sleep_ms(10)
                        # ble.ble_send_string("OK\r\n")
                        # utime.sleep_ms(10)
                        # 重启系统
                        Power.powerRestart()
                except (ValueError, KeyError) as e:
                    # 捕获JSON解析错误
                    printf("解析JSON时发生错误:{0}".format(e))
            elif "AT+UM982=" in ble.at_message:
                # 处理UM982命令
                with lock:
                    start_index = ble.at_message.index('=') + 1
                    end_index = ble.at_message.index('\r\n', start_index)
                    instruct = ble.at_message[start_index:end_index]
                    # 发送UM982指令
                    um982.uart_um982.write(instruct + "\r\n")
                    ble.ble_send_string("OK\r\n")
                    # ble.ble_send_string("OK\r\n")
                    # ble.ble_send_string("OK\r\n")
            elif "AT+UPDATE=" in ble.at_message:
                # 处理更新命令
                with lock:
                    if stop == True:
                        # 停止线程
                        _thread.stop_thread(rtcmsocket.thread_id)
                        um982.uart_um982.close()
                        _thread.stop_thread(um982.thread_id)
                        _thread.stop_thread(ble.main_thread_id)
                        stop = False
                    printf("states" + str(stop))
                    # 执行更新
                    appfota.update_code()
            elif "AT+GetUpdate4G" in ble.at_message:
                # 获取4G更新状态
                with lock:
                    if appfota.update_flag():
                        ble.uart_ble.write(xor_string("$UPDATE,TRUE"))
                    else:
                        ble.uart_ble.write(xor_string("$UPDATE,FALSE"))
                    ble.ble_send_string("OK\r\n")
                    # ble.ble_send_string("OK\r\n")
                    # ble.ble_send_string("OK\r\n")
        # 处理用户串口的AT命令
        elif ble.at_message_flat == 2:
            if "AT\r\n" in usruart.usr_at_message:
                # 如果是AT命令，返回OK
                usruart.usr_send_string("OK\r\n")
            elif "AT+Call=" in usruart.usr_at_message:
                # 处理打电话命令
                with lock:
                    start_index = usruart.usr_at_message.index('=') + 1
                    end_index = usruart.usr_at_message.index('\r\n', start_index)
                    instruct = usruart.usr_at_message[start_index:end_index]
                    
                    # um982.uart_um982.write(instruct + "\r\n")
                    printf(instruct)
                    
                    voiceCall.callEnd()
                    voiceCall.callEnd()
                    voiceCall.callEnd()
                    result = voiceCall.callStart(instruct)    # 打电话
                    if result == 0:
                        printf("电话拨打成功，正在呼出...")
                    else:
                        printf("电话拨打失败，错误码：{0}".format(result))
            elif "AT+Name=" in usruart.usr_at_message:
                # 处理设置串口名称的命令
                start_index = usruart.usr_at_message.index('=') + 1
                end_index = usruart.usr_at_message.index('\r\n', start_index)
                name = usruart.usr_at_message[start_index:end_index]
                printf("Extracted name: " + name)
                # 发送设置名称的命令
                usruart.uart_ble.write("AT+QBLENAME=" + name + "\r\n")
                usruart.usr_send_string("OK\r\n")
            elif "AT+{" in usruart.usr_at_message:
                try:
                    # 处理带有JSON数据的AT命令
                    json_part = usruart.usr_at_message[usruart.usr_at_message.index('{'):usruart.usr_at_message.index('}') + 1]
                    data = ujson.loads(json_part)

                    if "ip" in data and "port" in data and "mount" in data and "accpas" in data:
                        # 将配置写入文件并打印
                        fs.WriteFile("cors.txt", json_part)
                        FileContent = fs.ReadFile("cors.txt")
                        printf(FileContent)
                        printf("系统即将重启...")
                        usruart.usr_send_string("系统即将重启...")
                        usruart.usr_send_string("OK\r\n")
                        utime.sleep_ms(10)
                        usruart.usr_send_string("OK\r\n")
                        utime.sleep_ms(10)
                        usruart.usr_send_string("OK\r\n")
                        utime.sleep_ms(10)
                        # 重启系统
                        Power.powerRestart()
                except (ValueError, KeyError) as e:
                    # 捕获JSON解析错误
                    printf("解析JSON时发生错误:{}".format(e))
            elif "AT+UM982=" in usruart.usr_at_message:
                # 处理UM982命令
                with lock:
                    start_index = usruart.usr_at_message.index('=') + 1
                    end_index = usruart.usr_at_message.index('\r\n', start_index)
                    instruct = usruart.usr_at_message[start_index:end_index]
                    # 发送UM982指令
                    um982.uart_um982.write(instruct + "\r\n")
                    usruart.usr_send_string("OK\r\n")
            elif "AT+UPDATE=" in usruart.usr_at_message:
                # 处理更新命令
                with lock:
                    if stop == True:
                        # 停止相关线程
                        _thread.stop_thread(rtcmsocket.thread_id)
                        um982.uart_um982.close()
                        _thread.stop_thread(um982.thread_id)
                        _thread.stop_thread(ble.main_thread_id)
                        stop = False
                    printf("states" + str(stop))
                    # 执行更新
                    appfota.update_code()
            elif "AT+GetUpdate4G" in usruart.usr_at_message:
                # 获取4G更新状态
                with lock:
                    if appfota.update_flag():
                        usruart.uart_usr.write(xor_string("$UPDATE,TRUE"))
                    else:
                        usruart.uart_usr.write(xor_string("$UPDATE,FALSE"))
                    usruart.usr_send_string("OK\r\n")

        # 重置蓝牙消息的状态
        ble.at_message_flat = 0
