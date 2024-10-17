from machine import UART
import utime
import _thread
from misc import Power

import sys
# 添加 /usr 目录到模块搜索路径
sys.path.append('/usr')
import bleat
import um982

# 定义全局标志位
is_connected = False  # 初始状态为未连接


uart_ble = None
received = ""
at_message = ""
thread_id = None
main_thread_id = None

# 创建信号量
ble_read_semphore = _thread.allocate_semphore(1)


def printf(s):
    print("[ble]: " + s)


def init_ble():
    
    global uart_ble
    global thread_id
    
    # 开启蓝牙线程
    thread_id = _thread.start_new_thread(BLE_thread, (uart_ble,))
    uart_ble = UART(UART.UART2, 115200, 8, 0, 1, 0)  # 串口初始化
    uart_ble.set_callback(uart_call)  # 设置接收中断
    
    printf("ble完成初始化\r\n")
    ble_send_string("BLE初始化完成\r\n")
    
    return uart_ble  # 返回 UART 实例，以便在其他地方使用

# 蓝牙线程
def BLE_thread(para):
    global received
    global is_connected  # 使用全局变量
    global at_message
    while True:
        ble_read_semphore.acquire()
        
        
        message = received.decode('utf-8')  # 解码接收到的数据
        printf("信号量" + message)
        # 判断连接状态
        if "+CONNECTED" in message:
            is_connected = True  # 设置连接标志位为True
        elif "+DISCONNECTED" in message:
            is_connected = False  # 设置连接标志位为False
        
        # if message.startswith("AT") and message.endswith("\r\n"):
        #     at_message = message
        #     bleat.at_semaphore.release()  # 释放AT指令信号量
            
        try:
            # 去除前后空格并按行拆分
            nmea_lines = message.strip().split('\r\n')

            # 逐行处理 NMEA 消息
            for line in nmea_lines:
                if line.startswith("AT"):
                    printf("---------------------------------------------------------------------------" + line)
                    
                    at_message = line + "\r\n"  # 保存AT指令

                    # 释放AT指令信号量
                    bleat.at_semaphore.release()
                    
        except AttributeError as e:
            # 如果 message 是 None 或者 message.strip() 出现问题
            print("AttributeError in process_nmea_message: " + e)
        except RuntimeError as e:
            # 如果信号量释放时出现问题
            print("RuntimeError in process_nmea_message: " + e)
        except Exception as e:
            # 捕获所有其他异常
            print("Unexpected error in process_nmea_message: " + e)

def uart_call(para):
    global received
    received = uart_ble.read()  # 读取所有可用数据
    if received:
        if thread_id!=0:
            try:
                um982.uart_um982.write(received)
                ble_read_semphore.release()  # 释放信号量
            except RuntimeError as e:
                print("释放信号量失败: ", e)
        

def ble_send_string(s):
    if not s:
        return
    if is_connected == True:
        uart_ble.write(s)

        
