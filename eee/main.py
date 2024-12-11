import utime  # type: ignore # 导入utime模块，用于延时
import _thread  # 导入_thread模块，用于多线程
import sys  # 导入sys模块，用于系统级操作
# 添加 /usr 目录到模块搜索路径
sys.path.append('/usr')  
import um982  # 导入um982模块，用于与硬件进行交互
import ble  # 导入蓝牙模块
import rtcmsocket  # 导入RTC通信套接字模块
import bleat  # 导入AT命令模块
import usruart  # 导入用户串口模块
import gpio  # 导入GPIO模块，用于控制GPIO引脚
import syslog   # type: ignore # 导入系统日志模块



# utime.sleep_ms(3000)  # 延时5秒，确保系统初始化
# 初始化RTC通信套接字
socket_rtcm = rtcmsocket.rtcm_tcp_client()

# 初始化蓝牙通信
uart_ble = ble.init_ble()  
# 初始化用户串口
uart_usr = usruart.init_usruart()  
# 发送三次 "OK" 确认初始化完成
ble.ble_send_string("OK\r\n")
utime.sleep_ms(100)
ble.ble_send_string("OK\r\n")
utime.sleep_ms(100)
ble.ble_send_string("OK\r\n")

# 初始化um982设备
uart_um982 = um982.init_um982()  
utime.sleep_ms(1100)



# 初始化AT命令处理
bleat.init_at()

# 初始化GPIO引脚，用于控制蓝牙AT和模块LED
Bluetooth_AT_Pin = gpio.gpio_out(9)  
ModuleLED_Pin = gpio.gpio_out(10)  
# 设置引脚为高电平（打开）
Bluetooth_AT_Pin.set()
ModuleLED_Pin.set()



# 用于打印带有标签的调试信息
def printf(s):
    print("[main_template]: " + s)


# 主线程函数
def main_thread():
    # voiceCall.callStart('13985821802')    # 打电话
    while True:
        utime.sleep_ms(500)  # 每500毫秒循环一次

        # 根据RTC通信套接字的连接状态设置不同的响应
        if rtcmsocket.is_connected == 0:    # 连接CORS失败/未连接
            rtcm_s = "连接CORS失败/未连接\r\n"
            syslog.SysLampSignalState = 0   # 连接CORS失败/未连接
        elif rtcmsocket.is_connected == 1:  # 连接CORS服务器成功
            rtcm_s = "连接CORS服务器成功\r\n"
            syslog.SysLampSignalState = 1   # 连接CORS服务器成功
        elif rtcmsocket.is_connected == 2:  # 与CORS服务器握手成功
            rtcm_s = "与CORS服务器握手成功"
            syslog.SysLampSignalState = 2   # 与CORS服务器握手成功
        elif rtcmsocket.is_connected == 3:  # 握手失败（账号或密码错误/过期）
            rtcm_s = "握手失败（账号或密码错误/过期）\r\n"
            syslog.SysLampSignalState = 3   # 握手失败（账号或密码错误/过期）
        
        # 将连接状态发送给蓝牙
        # ble.ble_send_string(rtcm_s)   # 引起串口冲突
        # printf(rtcm_s)
        
        utime.sleep_ms(500)  # 延时500毫秒

        # 打印版本信息
        # printf("我是版本1.0.0")
        import net
        print(">>>{0}".format(net.csqQueryPoll()))
        print("{0}<<<".format(net.getState()))
        


def switch_led(value):
    if value == 0:      # 连接CORS失败/未连接
        ModuleLED_Pin.style_1()
    elif value == 1:    # 连接CORS服务器成功
        ModuleLED_Pin.style_2()
    elif value == 2:    # 与CORS服务器握手成功
        ModuleLED_Pin.style_2()
    elif value == 3:    # 握手失败（账号或密码错误/过期）
        ModuleLED_Pin.style_1()
    else:
        utime.sleep_ms(10)
        
# LED控制线程
def led_control_thread():
    while True:
        switch_led(syslog.SysLampSignalState)

# 启动主线程
def main():
    # 启动主线程
    ble.main_thread_id = _thread.start_new_thread(main_thread, ())
    # 启动LED控制线程
    _thread.start_new_thread(led_control_thread, ())

if __name__ == "__main__":
    # 系统初始化完成后，发送初始化完成信息
    # ble.ble_send_string("System initialization is complete!")  
    # 调用主函数启动程序
    main()
