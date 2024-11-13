import utime
import _thread
import ujson
from misc import Power

import sys
# 添加 /usr 目录到模块搜索路径
sys.path.append('/usr')
import um982
import ble
import fs
import rtcmsocket
import appfota
import usruart


# 创建信号量
at_semaphore = _thread.allocate_semphore(1)
thread_id = None

stop = True


def printf(s):
    print("[ble_at]: " + s)




def init_at():
    global thread_id
    # 开启AT线程
    thread_id = _thread.start_new_thread(AT_thread, ())


def xor_string(s):
    result = 0
    for char in s:
        result ^= ord(char)  # 对每个字符的ASCII值进行异或运算
    hex_result = "{:02x}".format(result).upper()  # 格式化为两位十六进制
    return s + "*" + hex_result + "\r\n"  # 直接返回十六进制字符串

# 创建一个锁对象
lock = _thread.allocate_lock()
def AT_thread():
    global stop
    while True:
        # 获取信号量
        at_semaphore.acquire()
        
        printf("信号量" + ble.at_message + str(ble.at_message_flat))
        
        if(ble.at_message_flat == 1):
            # 蓝牙串口
            if "AT\r\n" in ble.at_message:
                ble.ble_send_string("OK\r\n")
            elif "AT+Name=" in ble.at_message:
                # 提取名称部分
                start_index = ble.at_message.index('=') + 1
                end_index = ble.at_message.index('\r\n', start_index)
                name = ble.at_message[start_index:end_index]
                printf("Extracted name: " + name)
                ble.uart_ble.write("AT+QBLENAME=" + name + "\r\n")
                
                ble.ble_send_string("OK\r\n")
                ble.ble_send_string("OK\r\n")
                ble.ble_send_string("OK\r\n")
            elif "AT+{" in ble.at_message:
                try:
                    # 提取JSON部分
                    json_part = ble.at_message[ble.at_message.index('{'):ble.at_message.index('}') + 1]
                    # 解析JSON
                    data = ujson.loads(json_part)
                    
                    # 检查键是否存在
                    if "ip" in data and "port" in data and "mount" in data and "accpas" in data:
                        # 写入JSON内容到文件
                        fs.WriteFile("cors.txt", json_part)
                        FileContent = fs.ReadFile("cors.txt")
                        printf(FileContent)
                        printf("系统即将重启...")
                        ble.ble_send_string("系统即将重启...")
                        ble.ble_send_string("OK\r\n")
                        utime.sleep_ms(10)
                        ble.ble_send_string("OK\r\n")
                        utime.sleep_ms(10)
                        ble.ble_send_string("OK\r\n")
                        utime.sleep_ms(10)
                        # 重启系统 
                        Power.powerRestart()
                except (ValueError, KeyError) as e:
                    printf("解析JSON时发生错误:", e)
            elif "AT+UM982=" in ble.at_message:
                # 使用锁来保护代码块
                with lock:
                    # 提取指令部分
                    start_index = ble.at_message.index('=') + 1
                    end_index = ble.at_message.index('\r\n', start_index)
                    instruct = ble.at_message[start_index:end_index]
                    um982.uart_um982.write(instruct + "\r\n")
                    ble.ble_send_string("OK\r\n")
                    ble.ble_send_string("OK\r\n")
                    ble.ble_send_string("OK\r\n")
            elif "AT+UPDATE=" in ble.at_message:
                # 使用锁来保护代码块
                with lock:
                    if stop == True:
                        _thread.stop_thread(rtcmsocket.thread_id)
                        um982.uart_um982.close()
                        _thread.stop_thread(um982.thread_id)
                        _thread.stop_thread(ble.main_thread_id)
                        stop = False
                    printf("states" + str(stop))
                    
                    appfota.update_code()
                    
            elif "AT+GetUpdate4G" in ble.at_message:
                # 使用锁来保护代码块
                with lock:
                    if(appfota.update_flag()):
                        ble.uart_ble.write(xor_string("$UPDATE,TRUE"))
                    else:
                        ble.uart_ble.write(xor_string("$UPDATE,FALSE"))
                    ble.ble_send_string("OK\r\n")
                    ble.ble_send_string("OK\r\n")
                    ble.ble_send_string("OK\r\n")
        elif(ble.at_message_flat == 2):
            # 用户串口
            if "AT\r\n" in usruart.usr_at_message:
                usruart.usr_send_string("OK\r\n")
            elif "AT+Name=" in usruart.usr_at_message:
                # 提取名称部分
                start_index = usruart.usr_at_message.index('=') + 1
                end_index = usruart.usr_at_message.index('\r\n', start_index)
                name = usruart.usr_at_message[start_index:end_index]
                printf("Extracted name: " + name)
                usruart.uart_ble.write("AT+QBLENAME=" + name + "\r\n")
                
                usruart.usr_send_string("OK\r\n")
            elif "AT+{" in usruart.usr_at_message:
                try:
                    # 提取JSON部分
                    json_part = usruart.usr_at_message[usruart.usr_at_message.index('{'):usruart.usr_at_message.index('}') + 1]
                    # 解析JSON
                    data = ujson.loads(json_part)
                    
                    # 检查键是否存在
                    if "ip" in data and "port" in data and "mount" in data and "accpas" in data:
                        # 写入JSON内容到文件
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
                    printf("解析JSON时发生错误:", e)
            elif "AT+UM982=" in usruart.usr_at_message:
                # 使用锁来保护代码块
                with lock:
                    # 提取指令部分
                    start_index = usruart.usr_at_message.index('=') + 1
                    end_index = usruart.usr_at_message.index('\r\n', start_index)
                    instruct = usruart.usr_at_message[start_index:end_index]
                    um982.uart_um982.write(instruct + "\r\n")
                    usruart.usr_send_string("OK\r\n")
            elif "AT+UPDATE=" in usruart.usr_at_message:
                # 使用锁来保护代码块
                with lock:
                    if stop == True:
                        _thread.stop_thread(rtcmsocket.thread_id)
                        um982.uart_um982.close()
                        _thread.stop_thread(um982.thread_id)
                        _thread.stop_thread(ble.main_thread_id)
                        stop = False
                    printf("states" + str(stop))
                    
                    appfota.update_code()
                    
            elif "AT+GetUpdate4G" in usruart.usr_at_message:
                # 使用锁来保护代码块
                with lock:
                    if(appfota.update_flag()):
                        usruart.uart_usr.write(xor_string("$UPDATE,TRUE"))
                    else:
                        usruart.uart_usr.write(xor_string("$UPDATE,FALSE"))
                    usruart.usr_send_string("OK\r\n")
                    
                    
        ble.at_message_flat = 0
                
                

                
            
        
            
    