from machine import UART # type: ignore
import _thread
import sys
# 添加 /usr 目录到模块搜索路径，以便导入自定义模块
sys.path.append('/usr')
import bleat
import um982

# 定义全局标志位
is_connected = False  # 初始状态为未连接

uart_ble = None  # 蓝牙串口对象
received = ""  # 存储接收到的数据
at_message = ""  # 存储 AT 指令
thread_id = None  # 蓝牙线程 ID
main_thread_id = None  # 主线程 ID
at_message_flat = 0  # AT 指令标志

# 创建信号量，用于线程同步
ble_read_semphore = _thread.allocate_semphore(1)

def printf(s):
    """ 打印蓝牙信息的函数 """
    print("[ble]: " + s)

def init_ble():
    """ 初始化蓝牙模块和串口，并开启蓝牙接收线程 """
    global uart_ble
    global thread_id
    
    # 开启蓝牙接收线程
    thread_id = _thread.start_new_thread(BLE_thread, (uart_ble,))
    
    # 串口初始化：UART2，波特率115200，数据位8位，无校验，停止位1
    uart_ble = UART(UART.UART2, 115200, 8, 0, 1, 0)
    
    # 设置 UART 串口的接收中断回调函数
    uart_ble.set_callback(uart_call)
    
    printf("ble完成初始化\r\n")
    
    # 发送初始化完成的提示信息
    # ble_send_string("BLE初始化完成\r\n")
    
    return uart_ble  # 返回 UART 实例，以便在其他地方使用

# 蓝牙接收线程
def BLE_thread(para):
    global received
    global is_connected  # 使用全局变量
    global at_message
    global at_message_flat
    while True:
        # 等待信号量，确保不会发生数据竞争
        ble_read_semphore.acquire()
        
        # 解码接收到的数据
        message = received.decode('utf-8')
        printf("信号量 " + message)
        
        # 判断蓝牙连接状态
        if "+CONNECTED" in message:
            is_connected = True  # 设置为已连接
        elif "+DISCONNECTED" in message:
            is_connected = False  # 设置为未连接
        
        try:
            # 去除前后空格并按行拆分
            nmea_lines = message.strip().split('\r\n')

            # 逐行处理 NMEA 消息
            for line in nmea_lines:
                if line.startswith("AT"):  # 如果是 AT 指令
                    printf("---------------------------------------------------------------------------" + line)
                    
                    at_message = line + "\r\n"  # 保存AT指令

                    at_message_flat = 1  # 标记有新的 AT 指令
                    # 释放 AT 指令信号量
                    bleat.at_semaphore.release()
                    
        except AttributeError as e:
            # 处理异常：如果 message 是 None 或者 message.strip() 出现问题
            print("AttributeError in process_nmea_message: " + str(e))
        except RuntimeError as e:
            # 处理异常：如果信号量释放时出现问题
            print("RuntimeError in process_nmea_message: " + str(e))
        except Exception as e:
            # 捕获所有其他异常
            print("Unexpected error in process_nmea_message: " + str(e))

# 串口接收中断回调函数
def uart_call(para):
    global received
    received = uart_ble.read()  # 读取所有可用数据
    if received:
        if thread_id != 0:
            try:
                tempstr = received.decode('utf-8')  # 解码接收到的数据
                
                printf(tempstr)  # 打印接收到的消息
                
                # 如果接收到的是连接或断开消息或 AT 指令，释放信号量
                if "+CONNECTED" in tempstr or "+DISCONNECTED" in tempstr or "AT+" in tempstr:
                    ble_read_semphore.release()  # 释放信号量
                else:
                    # 将数据发送到 um982 模块
                    um982.uart_um982.write(received)
                
            except RuntimeError as e:
                print("释放信号量失败: ", e)

# 发送蓝牙字符串，若蓝牙已连接才发送
def ble_send_string(s):
    """ 发送字符串到蓝牙设备 """
    if not s:
        return  # 如果没有要发送的字符串，直接返回
    if is_connected == True:
        uart_ble.write(s)  # 向蓝牙串口写入数据
