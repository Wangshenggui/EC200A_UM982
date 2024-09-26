from machine import UART
import utime
import _thread


# 定义全局标志位
is_connected = False  # 初始状态为未连接


uart_ble = None

ble_send_data_list = [
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
    global uart_ble
    uart_ble = UART(UART.UART2, 115200, 8, 0, 1, 0)  # 串口初始化
    _thread.start_new_thread(ble_receive_data, (uart_ble,))
    
    for data in ble_send_data_list:
        utime.sleep_ms(1000)
        print(data)
        uart_ble.write(data)
    
    return uart_ble  # 返回 UART 实例，以便在其他地方使用


def string_to_hex(s):
    # 计算字符串的字符数
    char_count = len(s)
    
    # 将字符数转换为16进制，转为字符串格式并连接
    hex_value = ''
    for c in s:
        hex_value += '{:02x}'.format(ord(c))  # 将每个字符转换为16进制，并拼接
    
    # 创建最终的返回值
    result = "AT+QBLEGATTSNTFY=0,fff2," + str(char_count) + "," + hex_value + "\r\n"
    
    return result

def ble_send_string(s):
    result = string_to_hex(s)
    print(result)
    uart_ble.write(result)

def ble_receive_data(uart):
    global is_connected  # 使用全局变量
    
    while True:
        if uart.any():  # 检查是否有数据可读
            received = uart.read()  # 读取所有可用数据
            if received:
                message = received.decode('utf-8')  # 解码接收到的数据
                print("ble接收数据:", message)  # 打印接收到的数据
                
                # 判断连接状态
                if "+QBLESTAT:CONNECTED" in message:
                    is_connected = True  # 设置连接标志位为True
                    print("设备已连接")
                
                elif "+QBLESTAT:DISCONNECTED" in message:
                    is_connected = False  # 设置连接标志位为False
                    print("设备已断开连接")

        utime.sleep_ms(10)  # 避免占用过多 CPU
        
