from machine import UART
import utime
import _thread


ble_send_data_list = [
    "AT+QRST\r\n",
    "AT+QRST\r\n",
    "AT+QRST\r\n",
    "AT+QBLEINIT=2\r\n",
    "AT+QBLEADVPARAM=150,150\r\n",
    "AT+QBLEGATTSSRV=fff1\r\n",
    "AT+QBLEGATTSCHAR=fff2\r\n",
    "AT+QBLEGATTSCHAR=fff3\r\n",
    "AT+QBLEGATTSSRVDONE\r\n",
    "AT+QBLENAME=AiNiMa\r\n",
    "AT+QBLEADVSTART\r\n"
    ]

def init_ble():
    print("ble初始化\r\n")
    uart_ble = UART(UART.UART2, 115200, 8, 0, 1, 0)  # 串口初始化
    _thread.start_new_thread(ble_receive_data, (uart_ble,))
    
    for data in ble_send_data_list:
        utime.sleep_ms(1000)
        print(data)
        uart_ble.write(data)
    
    return uart_ble  # 返回 UART 实例，以便在其他地方使用


def ble_receive_data(uart):
    while True:
        if uart.any():  # 检查是否有数据可读
            received = uart.read()  # 读取所有可用数据
            if received:
                print("ble接收数据:", received.decode('utf-8'))  # 解码并打印接收到的数据
        utime.sleep_ms(100)  # 避免占用过多 CPU
