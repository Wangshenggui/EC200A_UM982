from machine import UART
import utime
import _thread
import sys
# 添加 /usr 目录到模块搜索路径
sys.path.append('/usr')
import um982
import ble
import fs
import rtcmsocket


# 初始化 um982
uart_um982 = um982.init_um982()
# 初始化rtcm_socket
socket_rtcm = rtcmsocket.rtcm_tcp_client("120.253.226.97",8002)
# 初始化 ble
uart_ble = ble.init_ble()


if __name__ == "__main__":
    
    # fs.CreateFile("um982.ini")   # 创建配置文件
    # fs.CreateFile("ble.ini")   # 创建配置文件
    
    # fs.ReadFile("um982.ini")
    # fs.ReadFile("ble.ini")

    
    while True:
        utime.sleep_ms(1000)
        if ble.is_connected:
            print("设备处于连接状态，可以发送数据\r\n")
            ble.ble_send_string(um982.um982_read_data)
        else:
            print("设备未连接，无法发送数据\r\n")
