from machine import UART
import utime
import _thread

import sys
# 添加 /usr 目录到模块搜索路径
sys.path.append('/usr')
import bleat

# 定义全局标志位
is_connected = False  # 初始状态为未连接


uart_ble = None
BLE_SYS_Command = 0
received = ""

# 创建信号量
ble_read_semphore = _thread.allocate_semphore(1)


def printf(s):
    print("[ble]: " + s)

ble_send_data_list = [
    "AT+QRST\r\n",  #复位
    "AT+QBLEINIT=2\r\n",    #模块为外围设备进行 BLE 初始化
    "AT+QBLEADVPARAM=150,150\r\n",  #设置 BLE 广播参数
    "AT+QBLEGATTSSRV=fff1\r\n", #创建 BLE 服务并设置服务 UUID 为 fff1
    "AT+QBLEGATTSCHAR=fff2\r\n",    #设置 GATT 特征值 UUID 为 fff2
    "AT+QBLEGATTSCHAR=fff3\r\n",    #设置 GATT 特征值 UUID 为 fff3
    "AT+QBLEGATTSSRVDONE\r\n",  #服务添加完成
    # "AT+QBLENAME=UM982_RTK\r\n",
    "AT+QBLEADVSTART\r\n",   #开启 BLE 广播
    ]

def init_ble():
    printf("ble初始化\r\n")
    global uart_ble
    
    # 开启蓝牙线程
    _thread.start_new_thread(BLE_thread, (uart_ble,))
    uart_ble = UART(UART.UART2, 115200, 8, 0, 1, 0)  # 串口初始化
    uart_ble.set_callback(uart_call)  # 设置接收中断
    
    for data in ble_send_data_list:
        utime.sleep_ms(800)
        printf(data)
        uart_ble.write(data)
    
    printf("ble完成初始化\r\n")
    ble_send_string("BLE初始化完成\r\n")
    
    return uart_ble  # 返回 UART 实例，以便在其他地方使用

# 蓝牙线程
def BLE_thread(para):
    global received
    global is_connected  # 使用全局变量
    global BLE_SYS_Command
    
    while True:
        ble_read_semphore.acquire()
        printf("信号量")
        
        message = received.decode('utf-8')  # 解码接收到的数据
        # 判断连接状态
        if "+QBLESTAT:CONNECTED" in message:
            is_connected = True  # 设置连接标志位为True
        elif "+QBLESTAT:DISCONNECTED" in message:
            is_connected = False  # 设置连接标志位为False
        
        if message.startswith("AT") and message.endswith("\r\n"):
            bleat.at_semaphore.release()  # 释放AT指令信号量

            
            
        
        

def uart_call(para):
    global received
    received = uart_ble.read()  # 读取所有可用数据
    if received:
        ble_read_semphore.release()  # 释放信号量
        
        

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
    if not s:
        return
    result = string_to_hex(s)
    uart_ble.write(result)

        
