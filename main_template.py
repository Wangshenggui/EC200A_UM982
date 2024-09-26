
import utime
import _thread
import sys
# 添加 /usr 目录到模块搜索路径
sys.path.append('/usr')
import um982


# 初始化 UART1
uart_um982 = um982.init_um982()

if __name__ == "__main__":

    # 启动接收线程
    _thread.start_new_thread(um982.receive_data, (uart_um982,))
    
    while True:
        utime.sleep_ms(500)
        print("主线程在运行\r\n")
