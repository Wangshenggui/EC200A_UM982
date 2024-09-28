from machine import UART
import utime
import _thread

import sys
sys.path.append('/usr')
import rtcmsocket


uart_um982 = None
um982_read_data = None
global_gga_data = None

received = ""

# 创建信号量
um982_read_semphore = _thread.allocate_semphore(1)

um982_send_data_list = [
    # "freset\r\n",
    "GPGGA COM1 1\r\n",
    "GPGGA COM2 1\r\n",
    "GPRMC COM1 1\r\n",
    "GPRMC COM2 1\r\n",
    "GPTHS COM1 1\r\n",
    "GPTHS COM2 1\r\n",
    "unmask BDS\r\n",
    "unmask GLO\r\n",
    "unmask GPS\r\n",
    "unmask GAL\r\n",
    "CONFIG ANTENNA2 ENABLE\r\n",
    # "saveconfig\r\n"
    ]

def printf(s):
    print("[um982]: " + s)

def init_um982():
    printf("um982初始化\r\n")
    global uart_um982
    
    # 开启UM982线程
    _thread.start_new_thread(UM982_thread, (uart_um982,))
    uart_um982 = UART(UART.UART1, 115200, 8, 0, 1, 0)  # 串口初始化
    uart_um982.set_callback(uart_call)  # 设置接收中断
    
    for data in um982_send_data_list:
        utime.sleep_ms(10)
        printf(data)
        uart_um982.write(data)
        
    
    
    return uart_um982  # 返回 UART 实例，以便在其他地方使用

# UM982线程
def UM982_thread(para):
    global global_gga_data
    global um982_read_data
    while True:
        um982_read_semphore.acquire()
        printf("信号量")
        
        um982_read_data = received.decode('utf-8')
        # 分离数据
        nmea_lines = um982_read_data.strip().split('\n')
        for line in nmea_lines:
            if line.startswith('$GNGGA'):  # 只处理 GGA 数据
                global_gga_data = line

def uart_call(para):
    global received
    received = uart_um982.read()  # 读取所有可用数据
    if received:
        um982_read_semphore.release()
        

        

