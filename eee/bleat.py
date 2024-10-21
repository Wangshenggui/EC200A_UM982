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


# 创建一个锁对象
lock = _thread.allocate_lock()
def AT_thread():
    global stop
    while True:
        # 获取信号量
        at_semaphore.acquire()
        
        printf("信号量" + ble.at_message)
        
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

                
            
        
            
    