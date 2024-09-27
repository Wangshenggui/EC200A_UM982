from machine import UART
import utime
import _thread

import sys
sys.path.append('/usr')
import rtcmsocket


uart_um982 = None
um982_read_data = None
global_gga_data = None

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



def init_um982():
    print("um982初始化\r\n")
    global uart_um982
    uart_um982 = UART(UART.UART1, 115200, 8, 0, 1, 0)  # 串口初始化
    uart_um982.set_callback(uart_call)  # 设置接收中断
    
    for data in um982_send_data_list:
        utime.sleep_ms(10)
        print(data)
        uart_um982.write(data)
    
    return uart_um982  # 返回 UART 实例，以便在其他地方使用

def uart_call(para):
    global global_gga_data
    global um982_read_data
    received = uart_um982.read()  # 读取所有可用数据
    if received:
        um982_read_data = received.decode('utf-8')
        print(um982_read_data)  # 解码并打印接收到的数据
        
        # 分离数据
        nmea_lines = um982_read_data.strip().split('\n')
        for line in nmea_lines:
            if line.startswith('$GNGGA'):  # 只处理 GGA 数据
                global_gga_data = line
                if rtcmsocket.is_connected: # 判断TCP是否连接
                    print("发送GGA到服务器")
                    rtcmsocket.rtcm_sock.send(global_gga_data + "\r\n")
                else:
                    print("未连接RTCM服务器")
        

        

