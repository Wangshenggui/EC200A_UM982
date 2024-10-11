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
utime.sleep_ms(10000)


from ftplib import FTP

def fetch_file_list(ftp_url, directory):
    ftp = None  # 在这里初始化 ftp 变量
    try:
        # 连接到 FTP 服务器
        ftp = FTP(ftp_url)
        ftp.login()  # 使用匿名登录
        ftp.cwd(directory)  # 切换到目标目录
        
        # 获取文件列表
        files = ftp.nlst()  # 获取目录下所有文件名
        # 过滤出 .txt 和 .py 文件
        filtered_files = [f for f in files if f.endswith('.txt') or f.endswith('.py')]
        
        # 打印获取到的文件名
        print("获取到的文件名: {}".format(", ".join(filtered_files)))
        
        return filtered_files
    except Exception as e:
        print("无法获取文件列表: {}".format(e))
        return []
    finally:
        if ftp:
            ftp.quit()  # 确保在结束时关闭连接

if __name__ == "__main__":
    ftp_url = '47.109.46.41'  # FTP 服务器地址
    directory = '/QuecPythonSourceCode/'  # 目标目录
    files = fetch_file_list(ftp_url, directory)

    # 生成下载列表
    download_list = [{'url': 'http://%s/FTP/QuecPythonSourceCode/%s' % (ftp_url, file), 
                      'file_name': '/usr/%s' % file}
                     for file in files]

    fota = app_fota.new()
    fota.bulk_download(download_list)  # 下载
    fota.set_update_flag()  # 设置升级标志
    Power.powerRestart()  # 重启设备

