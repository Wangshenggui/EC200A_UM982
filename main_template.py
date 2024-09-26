
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
    
    while True:
        utime.sleep_ms(500)
        print("主线程在运行\r\n")
