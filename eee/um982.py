from machine import UART # type: ignore
import _thread

import sys
sys.path.append('/usr')
import ble
import usruart

# 调试
DEBUG = False


# 串口对象和全局变量定义
uart_um982 = None  # 串口实例
um982_read_data = None  # 存储从串口读取的数据
global_gga_data = ""  # 存储最新的 GGA 数据
thread_id = None  # 用于存储线程 ID

received = ""  # 存储接收到的数据

# 创建信号量，用于串口数据读取的同步
um982_read_semphore = _thread.allocate_semphore(1)

def printf(s):
    if DEBUG:
        print("[um982]: " + s)

# 初始化UM982串口和相关设置
def init_um982():
    printf("um982初始化\r\n")  # 输出初始化信息
    global uart_um982
    global thread_id
    
    # 开启UM982线程
    thread_id = _thread.start_new_thread(UM982_thread, (uart_um982,))
    uart_um982 = UART(UART.UART1, 115200, 8, 0, 1, 0)  # 串口初始化
    uart_um982.set_callback(uart_call)  # 设置接收中断
    
    return uart_um982  # 返回 UART 实例，以便在其他地方使用

# UM982线程，用于周期性发送命令和处理接收到的数据
def UM982_thread(para):
    global global_gga_data
    global um982_read_data
    # 串口发送第一个字节会有问题，直接发两次，默认开启GGA
    uart_um982.write("GPGGA 1\r\n")  # 启用 GPGGA 数据输出
    uart_um982.write("GPGGA 1\r\n")  # 再次发送确保成功
    
    # uart_um982.write("GPDTM 1.0\r\n")
    
    # uart_um982.write("GPGBS 1.0\r\n")
    
    # uart_um982.write("GPGGA 0.1\r\n")
    # uart_um982.write("GPGGAH 1.0\r\n")
    
    # uart_um982.write("GPGLL 1.0\r\n")
    # uart_um982.write("GPGLLH 1.0\r\n")
    
    # uart_um982.write("GPGNS 1.0\r\n")
    # uart_um982.write("GPGNSH 1.0\r\n")
    
    # uart_um982.write("GPGRS 1.0\r\n")
    # uart_um982.write("GPGRSH 1.0\r\n")
    
    # uart_um982.write("GPGSA 1.0\r\n")
    # uart_um982.write("GPGSAH 1.0\r\n")
    
    # uart_um982.write("GPGST 1.0\r\n")
    # uart_um982.write("GPGSTH 1.0\r\n")
    
    # uart_um982.write("GPGSV 1.0\r\n")
    # uart_um982.write("GPGSVH 1.0\r\n")
    
    # uart_um982.write("GPTHS 0.1\r\n")
    
    # uart_um982.write("GPRMC 0.1\r\n")
    # uart_um982.write("GPRMCH 1.0\r\n")
    
    # uart_um982.write("GPROT 1.0\r\n")
    
    # uart_um982.write("GPVTG 0.1\r\n")
    # uart_um982.write("GPVTGH 1\r\n")
    
    # uart_um982.write("GPZDA 1.0\r\n")
    flag = False
    while True:
        um982_read_semphore.acquire()  # 等待信号量，确保线程同步
        
        um982_read_data = received.decode('utf-8')  # 解码接收到的字节数据为字符串
        
        # 分离数据，按行处理
        nmea_lines = um982_read_data.strip().split('\r\n')
        for line in nmea_lines:
            if line.startswith('$GNGGA,'):  # 只处理 GGA 数据
                global_gga_data = line  # 存储最新的 GGA 数据
                
                # 提取时间字段（位于第2个字段，格式为 HHMMSS.SSS）
                gga_fields = line.split(',')
                time_str = gga_fields[1]  # 获取时间字符串 (HHMMSS.SSS)
                if not time_str:
                    ble.uart_ble.write(line + "::")
                    ble.uart_ble.write("\r\n")  # 添加换行符
                    printf("无信号，退出循环")
                    break
                    
                if '.' in time_str:
                    integer_part, fractional_part = time_str.split('.')
                
                # 检查小数部分是否为50
                if fractional_part == '00':
                    flag = True
                    ble.uart_ble.write(line + "::")  # 将数据发送到蓝牙设备
                else:
                    flag = False
            if flag:
                prefixes = ('$GNGRS,', '$GNGRSH,', '$GNGSA,', '$GNGSAH,', '$GNGSV,', '$GNGSVH,')
                # if not any(line.startswith(prefix) for prefix in prefixes):
                ble.uart_ble.write(line + "::")

        ble.uart_ble.write("\r\n")  # 添加换行符
        usruart.uart_usr.write(um982_read_data)  # 将接收到的数据写入 usr 串口
        
        
        
        
# 串口数据接收中断回调函数
def uart_call(para):
    global received
    received = uart_um982.read()  # 读取所有可用数据
    if received:
        um982_read_semphore.release()  # 释放信号量，允许处理数据
        

        

