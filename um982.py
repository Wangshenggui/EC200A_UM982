from machine import UART
import utime
import _thread

import sys
sys.path.append('/usr')
import rtcmsocket
import fs
import ble


uart_um982 = None
um982_read_data = None
global_gga_data = ""

received = ""

# 创建信号量
um982_read_semphore = _thread.allocate_semphore(1)

# um982_send_data_list = \
# "GPGGA COM1 1\r\n\
# GPGGA COM2 1\r\n\
# GPRMC COM1 1\r\n\
# GPRMC COM2 1\r\n\
# GPTHS COM1 1\r\n\
# GPTHS COM2 1\r\n\
# unmask BDS\r\n\
# unmask GLO\r\n\
# unmask GPS\r\n\
# unmask GAL\r\n\
# CONFIG ANTENNA2 ENABLE\r\n"
    # "saveconfig\r\n"

# 从天线使能
# CONFIG ANTENNA2 ENABLE
# CONFIG ANTENNA2 DISABLE
# CONIFG ANTENNA2 DISABLE Lowpower

# 卫星跟踪和禁止
# MASK GPS            禁止接收机跟踪 GPS 卫星系统
# MASK BDS            禁止接收机跟踪 BDS 卫星系统
# MASK GLO            禁止接收机跟踪 GLO 卫星系统
# MASK GAL            禁止接收机跟踪 GAL 卫星系统
# MASK QZSS           禁止接收机跟踪 QZSS 卫星系统
# MASK 10             设置接收机跟踪卫星的截止角度为 10 度
# MASK 10             GPS 设置 GPS 卫星系统的截止角度为 10 度
# MASK 0              设置接收机跟踪卫星的截止角度为 0 度
# MASK B1             禁止接收机跟踪北斗卫星系统的 B1 频点信号
# MASK E5a            禁止接收机跟踪 Galileo 卫星系统的 E5a 频点信号
# MASK GPS PRN 10     禁止接收机跟踪 GPS 卫星系统的第 10 号卫星

# UNMASK GPS          使能接收机跟踪 GPS 卫星系统
# UNMASK BDS          使能接收机跟踪 BDS 卫星系统
# UNMASK GLO          使能接收机跟踪 GLO 卫星系统
# UNMASK GAL          使能接收机跟踪 GAL 卫星系统
# UNMASK B1           使能接收机跟踪北斗卫星系统的 B1 频点信号
# UNMASK E5a          使能接收机跟踪 Galileo 卫星系统的 E5a 频点信号

# NMEA消息V4.10
#     GPGNSH 1        当前串口输出 1Hz 的 GPGNSH 信息
#     GPGNSH COM2 1   在 com2 输出 1Hz 的 GPGNSH 信息
# GPDTM           坐标信息
# GPGBS           卫星故障检测信息
# GPGGA           卫星定位信息
# GPGGAH          从天线计算的卫星定位信息
# GPGLL           地理位置信息
# GPGLLH          从天线计算的地理位置信息
# GPGNS           定位数据输出
# GPGNSH          从天线计算的定位数据输出
# GPGRS           定位解算的卫星残差
# GPGRSH          从天线定位解算的卫星残差
# GPGSA           参与定位解算的卫星信息
# GPGSAH          从天线参与定位解算的卫星信息
# GPGST           伪距观测误差信息
# GPGSTH          从天线计算的伪距观测误差信息
# GPGSV           可视卫星信息
# GPGSVH          从天线的可视卫星信息输出
# GPTHS           航向信息
# GPRMC           卫星定位信息
# GPRMCH          从天线的卫星定位信息
# GPROT           旋转速度和方向信息
# GPVTG           地面航向与速度信息
# GPVTGH          从天线的地面航向与速度信息
# GPZDA           日期和时间

# 禁用串口输出
# UNLOG                       对当前串口停止输出所有的信息
# UNLOG GPGGA                 对当前串口停止输出 GPGGA 语句
# UNLOG COM1                  停止 com1 所有的信息输出
# UNLOG COM2 GPGGA            停止 com2 输出的 GPGGA 语句

# FRESET
#     清除保存的设置，卫星星历、位置信息等，并恢复接收机出厂设置，出厂设置波特率为115200bps
# RESET 重启接收机
#     EPHEM                   重启接收机，清除保存的卫星星历
#     IONUTC                  重启接收机，清除电离层和 UTC 参数
#     ALMANAC                 重启接收机，清除历书
#     POSITION                重启接收机，清除位置
#     Clockdrift              重启接收机， 清除接收机钟漂
#     ALL                     重启接收机， 清除以上所有信息，clockdrift除外
    
# SAVECONFIG
#     保存用户配置到非易失性存储器（NVM）中





def printf(s):
    print("[um982]: " + s)

def init_um982():
    printf("um982初始化\r\n")
    global uart_um982
    
    # 开启UM982线程
    _thread.start_new_thread(UM982_thread, (uart_um982,))
    uart_um982 = UART(UART.UART1, 115200, 8, 0, 1, 0)  # 串口初始化
    uart_um982.set_callback(uart_call)  # 设置接收中断
    
    # for data in um982_send_data_list:
    #     utime.sleep_ms(10)
    #     printf(data)
    #     uart_um982.write(data)
    
#     if fs.CreateFile("um982.txt") == True:
#         FileContent = fs.ReadFile("um982.txt")
#     else:
#         fs.WriteFile("um982.txt","GPGGA COM1 1\r\n\
# GPGGA COM2 1\r\n\
# GPRMC COM1 1\r\n\
# GPRMC COM2 1\r\n\
# GPTHS COM1 1\r\n\
# GPTHS COM2 1\r\n\
# unmask BDS\r\n\
# unmask GLO\r\n\
# unmask GPS\r\n\
# unmask GAL\r\n\
# CONFIG ANTENNA2 ENABLE\r\n")
#         FileContent = fs.ReadFile("um982.txt")
    
#     # 发送两次，有时候发送第一个字节会失败，导致出现错误
#     uart_um982.write(FileContent)
#     uart_um982.write(FileContent)
    
    
    return uart_um982  # 返回 UART 实例，以便在其他地方使用

# UM982线程
def UM982_thread(para):
    global global_gga_data
    global um982_read_data
    # 串口发送第一个字节会有问题，直接发两次，默认开启GGA
    uart_um982.write("GPGGA 1\r\n")
    
    # uart_um982.write("GPDTM 1\r\n")
    # uart_um982.write("GPGBS 1\r\n")
    uart_um982.write("GPGGA 1\r\n")
    # uart_um982.write("GPGGAH 1\r\n")
    # uart_um982.write("GPGLL 1\r\n")
    # uart_um982.write("GPGLLH 1\r\n")
    # uart_um982.write("GPGNS 1\r\n")
    # uart_um982.write("GPGNSH 1\r\n")
    # # uart_um982.write("GPGRS 1\r\n")
    # # uart_um982.write("GPGRSH 1\r\n")
    # # uart_um982.write("GPGSA 1\r\n")
    # # uart_um982.write("GPGSAH 1\r\n")
    # uart_um982.write("GPGST 1\r\n")
    # uart_um982.write("GPGSTH 1\r\n")
    # # uart_um982.write("GPGSV 1\r\n")
    # # uart_um982.write("GPGSVH 1\r\n")
    # uart_um982.write("GPTHS 1\r\n")
    # uart_um982.write("GPRMC 1\r\n")
    # uart_um982.write("GPRMCH 1\r\n")
    # uart_um982.write("GPROT 1\r\n")
    # uart_um982.write("GPVTG 1\r\n")
    # uart_um982.write("GPVTGH 1\r\n")
    # uart_um982.write("GPZDA 1\r\n")
    
# GPDTM           坐标信息
# GPGBS           卫星故障检测信息
# GPGGA           卫星定位信息
# GPGGAH          从天线计算的卫星定位信息
# GPGLL           地理位置信息
# GPGLLH          从天线计算的地理位置信息
# GPGNS           定位数据输出
# GPGNSH          从天线计算的定位数据输出
# GPGRS           定位解算的卫星残差
# GPGRSH          从天线定位解算的卫星残差
# GPGSA           参与定位解算的卫星信息
# GPGSAH          从天线参与定位解算的卫星信息
# GPGST           伪距观测误差信息
# GPGSTH          从天线计算的伪距观测误差信息
# GPGSV           可视卫星信息
# GPGSVH          从天线的可视卫星信息输出
# GPTHS           航向信息
# GPRMC           卫星定位信息
# GPRMCH          从天线的卫星定位信息
# GPROT           旋转速度和方向信息
# GPVTG           地面航向与速度信息
# GPVTGH          从天线的地面航向与速度信息
# GPZDA           日期和时间
    while True:
        um982_read_semphore.acquire()
        
        um982_read_data = received.decode('utf-8')
        
        # 分离数据
        nmea_lines = um982_read_data.strip().split('\n')
        for line in nmea_lines:
            if line.startswith('$GNGGA,'):  # 只处理 GGA 数据
                global_gga_data = line
                
            ble.ble_send_string(line)
            utime.sleep_ms(10)

def uart_call(para):
    global received
    received = uart_um982.read()  # 读取所有可用数据
    if received:
        um982_read_semphore.release()
        

        

