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


# 初始化 ble
uart_ble = ble.init_ble()
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

update_code_flag = False


def printf(s):
    print("[main_template]: " + s)
    


def read_file_from_ftp(ftp_url, directory, filename):
    file_content = ""  # 用于存储文件内容

    try:
        # 连接到 FTP 服务器
        ftp = FTP(ftp_url)
        ftp.login()  # 使用匿名登录
        ftp.cwd(directory)  # 切换到目标目录

        # 定义一个函数来处理数据块
        def handle_binary_data(data):
            nonlocal file_content  # 声明非局部变量
            file_content += data.decode('utf-8')  # 解码并添加到 file_content
        
        # 使用 retrbinary 方法读取文件内容
        command = 'RETR {}'.format(filename)  # 使用 str.format() 创建命令
        ftp.retrbinary(command, handle_binary_data)

    except Exception as e:
        print("无法读取文件: {}".format(e))
    finally:
        ftp.quit()  # 确保在结束时关闭连接

    return file_content  # 返回读取的文件内容


def compare_versions(version1, version2):
    # 将版本号分解为整数列表
    v1_parts = list(map(int, version1.split(".")))
    v2_parts = list(map(int, version2.split(".")))

    # 比较每一部分
    for v1, v2 in zip(v1_parts, v2_parts):
        if v1 < v2:
            return -1  # version1 < version2
        elif v1 > v2:
            return 1   # version1 > version2

    # 如果前面部分相同，比较长度
    if len(v1_parts) < len(v2_parts):
        return -1
    elif len(v1_parts) > len(v2_parts):
        return 1

    return 0  # version1 == version2
    
def main_thread():
    global update_code_flag
    
    text1 = fs.ReadFile("version.txt")
    printf("本地版本: " + text1)
    
    ftp_url = '47.109.46.41'  # FTP 服务器地址
    directory = '/QuecPythonSourceCode/'  # 目标目录
    filename = 'version.txt'  # 需要读取的文件名
    text2 = read_file_from_ftp(ftp_url, directory, filename)
    printf("服务器版本: " + text2)
    
    result = compare_versions(text1, text2)

    if result < 0:
        printf(text1 + " < " + text2)
        update_code_flag = True
    elif result > 0:
        printf(text1 + " > " + text2)
        update_code_flag = False
    else:
        printf(text1 + " = " + text2)
        update_code_flag = False
        
    if(update_code_flag):
        printf("有新版本")
    else:
        printf("不需要更新代码")
    

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
        
        if(update_code_flag):
            ble.ble_send_string("There are new versions that need to be updated!!!!!!!")
            printf("There are new versions that need to be updated!!!!!!!")
        
        
        printf("主线程")

def main():
    ble.main_thread_id = _thread.start_new_thread(main_thread, ())

if __name__ == "__main__":
    ble.ble_send_string("System initialization is complete!")
    
    main()
    
    
    
    

