from machine import UART
import utime
import _thread



um982_send_data_list = [
    # "freset\r\n",
    "GPGGA COM1 0.5\r\n",
    "GPGGA COM2 0.5\r\n",
    "GPRMC COM1 0.5\r\n",
    "GPRMC COM2 0.5\r\n",
    "unmask BDS\r\n",
    "unmask GLO\r\n",
    "unmask GPS\r\n",
    "unmask GAL\r\n",
    "CONFIG ANTENNA2 ENABLE\r\n"
    # "saveconfig\r\n"
    ]

def init_um982():
    print("um982初始化\r\n")
    uart_um982 = UART(UART.UART1, 115200, 8, 0, 1, 0)  # 串口初始化
    _thread.start_new_thread(um982_receive_data, (uart_um982,))
    
    for data in um982_send_data_list:
        utime.sleep_ms(10)
        print(data)
        uart_um982.write(data)
    
    return uart_um982  # 返回 UART 实例，以便在其他地方使用


def um982_receive_data(uart):
    while True:
        if uart.any():  # 检查是否有数据可读
            received = uart.read()  # 读取所有可用数据
            if received:
                print("um982接收数据:", received.decode('utf-8'))  # 解码并打印接收到的数据
        utime.sleep_ms(10)  # 避免占用过多 CPU
