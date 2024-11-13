from machine import UART
import _thread

import sys
# 添加 /usr 目录到模块搜索路径
sys.path.append('/usr')
import bleat
import ble



# 创建信号量
usr_read_semphore = _thread.allocate_semphore(1)

uart_usr = None
usr_thread_id = None
usr_received = ""
usr_at_message = ""


def printf(s):
    print("[usruart]: " + s)

# 初始化用户串口
def init_usruart():
    
    global uart_usr
    global usr_thread_id
    
    # 开启用户串口线程
    usr_thread_id = _thread.start_new_thread(USR_thread, (uart_usr,))
    uart_usr = UART(UART.UART0, 115200, 8, 0, 1, 0)  # 串口初始化
    uart_usr.set_callback(uart_call)  # 设置接收中断
    
    printf("usruart完成初始化\r\n")
    
    return uart_usr  # 返回 UART 实例，以便在其他地方使用

# 用户串口线程
def USR_thread(para):
    global usr_received
    global usr_at_message
    printf("yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy")
    while True:
        usr_read_semphore.acquire()
        
        
        message = usr_received.decode('utf-8')  # 解码接收到的数据
        printf("信号量" + message)
        
        try:
            # 去除前后空格并按行拆分
            nmea_lines = message.strip().split('\r\n')

            # 逐行处理 NMEA 消息
            for line in nmea_lines:
                if line.startswith("AT"):
                    printf("---------------------------------------------------------------------------" + line)
                    
                    usr_at_message = line + "\r\n"  # 保存AT指令

                    ble.at_message_flat = 2
                    # 释放AT指令信号量
                    bleat.at_semaphore.release()
                    
        except AttributeError as e:
            # 如果 message 是 None 或者 message.strip() 出现问题
            print("AttributeError in process_nmea_message: " + str(e))
        except RuntimeError as e:
            # 如果信号量释放时出现问题
            print("uRuntimeError in process_nmea_message: " + str(e))
        except Exception as e:
            # 捕获所有其他异常
            print("Unexpected error in process_nmea_message: " + str(e))


def uart_call(para):
    global usr_received
    usr_received = uart_usr.read()  # 读取所有可用数据
    if usr_received:
        if usr_thread_id!=0:
            try:
                tempstr = usr_received.decode('utf-8')  # 解码接收到的数据
                if "AT" in tempstr:
                    usr_read_semphore.release()  # 释放信号量
                
            except RuntimeError as e:
                print("释放信号量失败: ", e)
                
                
def usr_send_string(s):
    if not s:
        return
    uart_usr.write(s)
        
