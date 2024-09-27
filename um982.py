from machine import UART
import utime
import _thread


uart_um982 = None

um982_send_data_list = [
    # "freset\r\n",
    "GPGGA COM1 0.1\r\n",
    "GPGGA COM2 0.1\r\n",
    "GPRMC COM1 0.1\r\n",
    "GPRMC COM2 0.1\r\n",
    "unmask BDS\r\n",
    "unmask GLO\r\n",
    "unmask GPS\r\n",
    "unmask GAL\r\n",
    "CONFIG ANTENNA2 ENABLE\r\n"
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
    received = uart_um982.read()  # 读取所有可用数据
    if received:
        print("um982中断接收数据:", received.decode('utf-8'))  # 解码并打印接收到的数据

        

