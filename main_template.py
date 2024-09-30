from machine import UART
import utime
import _thread
from misc import Power
import sys
# 添加 /usr 目录到模块搜索路径
sys.path.append('/usr')
import um982
import ble
import fs
import rtcmsocket
import bleat



# 初始化 ble
uart_ble = ble.init_ble()
# 初始化 um982
uart_um982 = um982.init_um982()
utime.sleep_ms(1100)
# 初始化rtcm_socket
socket_rtcm = rtcmsocket.rtcm_tcp_client()
# 初始化AT
bleat.init_at()


def printf(s):
    print("[main_template]: " + s)

if __name__ == "__main__":
    
    # fs.CreateFile("um982.ini")   # 创建配置文件
    # fs.CreateFile("ble.ini")   # 创建配置文件
    
    # fs.ReadFile("um982.ini")
    # fs.ReadFile("ble.ini")

    ble.ble_send_string("System initialization is complete!")
    while True:
        utime.sleep_ms(1000)
        
        if rtcmsocket.is_connected == 0:
            rtcm_s = "No SIM card\r\n"
        elif rtcmsocket.is_connected == 1:
            rtcm_s = "Connected network\r\n"
        elif rtcmsocket.is_connected == 2:
            rtcm_s = ""
        elif rtcmsocket.is_connected == 3:
            rtcm_s = "Account password error\r\n"
        ble.ble_send_string(rtcm_s)
        
        if ble.BLE_SYS_Command == 1:
            ble.ble_send_string(um982.um982_read_data)
            
        printf("主线程")
        # Power.powerRestart()
