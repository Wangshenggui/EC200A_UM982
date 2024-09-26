from machine import UART
import utime
import _thread
import sys
# 添加 /usr 目录到模块搜索路径
sys.path.append('/usr')
import um982
import ble


# 初始化 um982
uart_um982 = um982.init_um982()
# 初始化 ble
uart_ble = ble.init_ble()

if __name__ == "__main__":
    
    num = 0  # 初始化数字
    while True:
        utime.sleep_ms(3000)
        if ble.is_connected:
            print("设备处于连接状态，可以发送数据")
            s=str(num)
            num+=1
            ble.ble_send_string(s + "," + s*2)
        else:
            print("设备未连接，无法发送数据")
