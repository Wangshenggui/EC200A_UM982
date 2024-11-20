from machine import UART
import _thread

import sys
# 添加 /usr 目录到模块搜索路径，方便后续引入自定义模块
sys.path.append('/usr')
import bleat
import ble

# 创建信号量，用于线程同步
usr_read_semphore = _thread.allocate_semphore(1)

# 定义全局变量
uart_usr = None  # 串口实例
usr_thread_id = None  # 用户串口线程 ID
usr_received = ""  # 存储接收到的用户串口数据
usr_at_message = ""  # 存储 AT 指令

# 打印调试信息的函数
def printf(s):
    print("[usruart]: " + s)

# 初始化用户串口函数
def init_usruart():
    global uart_usr
    global usr_thread_id
    
    # 启动用户串口线程
    usr_thread_id = _thread.start_new_thread(USR_thread, (uart_usr,))
    
    # 初始化 UART 实例，设置串口参数（波特率 115200，数据位 8，停止位 1，校验位 0）
    uart_usr = UART(UART.UART0, 115200, 8, 0, 1, 0)
    
    # 设置串口接收中断回调函数
    uart_usr.set_callback(uart_call)
    
    printf("usruart完成初始化\r\n")
    
    return uart_usr  # 返回串口实例，便于后续使用

# 用户串口线程，用于处理串口接收到的数据
def USR_thread(para):
    global usr_received
    global usr_at_message
    printf("用户串口线程已启动，开始接收数据")

    while True:
        # 等待信号量，确保串口数据处理同步
        usr_read_semphore.acquire()

        # 将接收到的字节数据解码为字符串
        message = usr_received.decode('utf-8')  
        printf("接收到的消息: " + message)
        
        try:
            # 去除消息前后的空格，并按行拆分
            nmea_lines = message.strip().split('\r\n')

            # 逐行处理 NMEA 消息
            for line in nmea_lines:
                if line.startswith("AT"):  # 如果是 AT 指令
                    printf("接收到的 AT 指令: " + line)
                    
                    usr_at_message = line + "\r\n"  # 保存 AT 指令

                    ble.at_message_flat = 2  # 设置 AT 消息标记
                    # 释放 AT 指令的信号量，通知其他线程处理 AT 指令
                    bleat.at_semaphore.release()
                    
        except AttributeError as e:
            # 处理 AttributeError 异常（例如数据为空或格式不对）
            print("AttributeError in process_nmea_message: " + str(e))
        except RuntimeError as e:
            # 处理 RuntimeError 异常（例如信号量释放失败）
            print("RuntimeError in process_nmea_message: " + str(e))
        except Exception as e:
            # 捕获其他未预见的异常
            print("Unexpected error in process_nmea_message: " + str(e))

# 串口接收中断回调函数，处理从串口接收到的数据
def uart_call(para):
    global usr_received
    # 读取串口接收到的数据
    usr_received = uart_usr.read()  
    
    if usr_received:  # 如果有数据接收
        if usr_thread_id != 0:  # 如果线程 ID 有效
            try:
                tempstr = usr_received.decode('utf-8')  # 解码接收到的数据为字符串
                if "AT" in tempstr:  # 如果数据中包含 AT 指令
                    usr_read_semphore.release()  # 释放信号量，唤醒处理线程
            except RuntimeError as e:
                # 捕获异常并打印错误信息
                print("释放信号量失败: ", e)

# 向用户串口发送字符串数据
def usr_send_string(s):
    if not s:
        return  # 如果字符串为空，则不进行任何操作
    uart_usr.write(s)  # 向串口发送数据
