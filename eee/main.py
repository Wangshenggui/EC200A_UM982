from machine import UART
import utime
import _thread
from misc import Power
from ftplib import FTP
import sys
# 添加 /usr 目录到模块搜索路径
sys.path.append('/usr')
import um982
import ble
import fs
import rtcmsocket
import bleat
import appfota
import usruart


utime.sleep_ms(5000)

# 初始化 ble
uart_ble = ble.init_ble()
uart_usr = usruart.init_usruart()
ble.ble_send_string("OK\r\n")
utime.sleep_ms(100)
ble.ble_send_string("OK\r\n")
utime.sleep_ms(100)
ble.ble_send_string("OK\r\n")
# 初始化 um982
uart_um982 = um982.init_um982()
utime.sleep_ms(1100)
# 初始化rtcm_socket
socket_rtcm = rtcmsocket.rtcm_tcp_client()
# 初始化AT
bleat.init_at()



def printf(s):
    print("[main_template]: " + s)
    

    
def main_thread():
    
    

    while True:
        utime.sleep_ms(500)
        
        if rtcmsocket.is_connected == 0:
            rtcm_s = "No SIM card\r\n"
        elif rtcmsocket.is_connected == 1:
            rtcm_s = "Connected network\r\n"
        elif rtcmsocket.is_connected == 2:
            rtcm_s = ""
        elif rtcmsocket.is_connected == 3:
            rtcm_s = "Account password error\r\n"
        ble.ble_send_string(rtcm_s)
        
        utime.sleep_ms(500)
        
        printf("我是版本1.0.0")
        

def main():
    ble.main_thread_id = _thread.start_new_thread(main_thread, ())

if __name__ == "__main__":
    ble.ble_send_string("System initialization is complete!")
    
    main()
    
    
    
    

