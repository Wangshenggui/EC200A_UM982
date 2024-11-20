# import app_fota
# from misc import Power
# import utime

# utime.sleep_ms(10000)


# if __name__ == "__main__":
#     fota = app_fota.new()
#     download_list = [
#         {'url': 'http://47.109.46.41/file_download/QuecPythonSourceCode/1.txt', 'file_name': '/usr/1.txt'},
#         {'url': 'http://47.109.46.41/file_download/QuecPythonSourceCode/ggg.py', 'file_name': '/usr/ggg.py'}, 
#         {'url': 'http://47.109.46.41/file_download/QuecPythonSourceCode/2.txt', 'file_name': '/usr/2.txt'}]
#     fota.bulk_download(download_list) # 下载
#     fota.set_update_flag() # 设置升级标志
#     Power.powerRestart()


import app_fota
from misc import Power
import utime

from ftplib import FTP
import fs


update_code_flag = False


def printf(s):
    print("[appfota]: " + s)

def read_file_from_ftp(ftp_url, directory, filename):
    file_content = ""

    try:
        # ftp = FTP(ftp_url)
        # ftp.login()
        # ftp.cwd(directory)
        
        # ///////////////////////////////////
        username = "QPyCode"
        password = "123456"
        # 连接到 FTP 服务器
        ftp = FTP(ftp_url)
        
        # 启用被动模式
        ftp.set_pasv(True)
        
        ftp.login(username, password)  # 使用指定用户名和密码登录
        ftp.cwd(directory)  # 切换到目标目录
        # ///////////////////////////////////

        def handle_binary_data(data):
            nonlocal file_content
            file_content += data.decode('utf-8')

        command = 'RETR {}'.format(filename)
        ftp.retrbinary(command, handle_binary_data)

    except OSError:
        print("无法连接，跳过文件读取。")
        return ""  # 直接返回空字符串
    except Exception as e:
        print("无法读取文件: {}".format(e))
        return ""  # 也返回空字符串以避免后续引用未赋值变量
    finally:
        try:
            ftp.quit()
        except:
            pass  # 确保即使在关闭连接时出错也不会影响程序

    return file_content



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

def update_flag():
    global update_code_flag
    
    text1 = fs.ReadFile("version.txt")
    # printf("本地版本: " + text1)
    
    ftp_url = '47.109.46.41'  # FTP 服务器地址
    directory = ''  # 目标目录
    filename = 'version.txt'  # 需要读取的文件名
    text2 = read_file_from_ftp(ftp_url, directory, filename)
    
    
    
    if (text2 == ""):
        text2 = text1
    # printf("服务器版本: " + text2)
    
    result = compare_versions(text1, text2)

    if result < 0:
        # printf(text1 + " < " + text2)
        update_code_flag = True
    elif result > 0:
        # printf(text1 + " > " + text2)
        update_code_flag = False
    else:
        # printf(text1 + " = " + text2)
        update_code_flag = False
        
    # if(update_code_flag):
    #     printf("有新版本")
    # else:
    #     printf("不需要更新代码")
    
    return update_code_flag

# def fetch_file_list(ftp_url, directory):
#     ftp = None  # 在这里初始化 ftp 变量
#     try:
#         # 连接到 FTP 服务器
#         ftp = FTP(ftp_url)
#         ftp.login()  # 使用匿名登录
#         ftp.cwd(directory)  # 切换到目标目录
        
#         # 获取文件列表
#         files = ftp.nlst()  # 获取目录下所有文件名
#         # 过滤出 .txt 和 .mpy 文件
#         filtered_files = [f for f in files if f.endswith('.txt') or f.endswith('.mpy')]
        
#         # 打印获取到的文件名
#         print("获取到的文件名: {}".format(", ".join(filtered_files)))
        
#         return filtered_files
#     except Exception as e:
#         print("无法获取文件列表: {}".format(e))
#         return []
#     finally:
#         if ftp:
#             ftp.quit()  # 确保在结束时关闭连接
            
def fetch_file_list(ftp_url, directory, username, password):
    ftp = None  # 初始化 FTP 对象
    try:
        # 连接到 FTP 服务器
        ftp = FTP(ftp_url)
        
        # 启用被动模式
        ftp.set_pasv(True)
        
        ftp.login(username, password)  # 使用指定用户名和密码登录
        ftp.cwd(directory)  # 切换到目标目录
        
        # 获取文件列表
        files = ftp.nlst()  # 获取目录下所有文件名
        # 过滤出 .txt 和 .mpy 文件
        filtered_files = [f for f in files if f.endswith('.txt') or f.endswith('.mpy')]
        
        # 打印获取到的文件名
        print("获取到的文件名: {}".format(", ".join(filtered_files)))
        
        return filtered_files
    except Exception as e:
        print("无法获取文件列表: {}".format(e))
        return []
    finally:
        if ftp:
            ftp.quit()  # 确保在结束时关闭连接

def update_code():
    ftp_url = "47.109.46.41"
    directory = ""
    username = "QPyCode"
    password = "123456"

    files = fetch_file_list(ftp_url, directory, username, password)

    # 生成下载列表
    download_list = [{'url': 'http://47.109.46.41/QPyCode/%s' % (file), 
                      'file_name': '/usr/%s' % file}
                     for file in files]

    fota = app_fota.new()
    fota.bulk_download(download_list)  # 下载
    fota.set_update_flag()  # 设置升级标志
    Power.powerRestart()  # 重启设备

