import app_fota
from misc import Power
import utime

from ftplib import FTP
import fs

# 代码更新标志
update_code_flag = False


def printf(s):
    """ 打印带有标签的信息 """
    print("[appfota]: " + s)

def read_file_from_ftp(ftp_url, directory, filename):
    """ 从 FTP 服务器读取指定文件内容
    
    参数:
    ftp_url (str): FTP 服务器的 URL 地址
    directory (str): 目标目录路径
    filename (str): 要读取的文件名

    返回:
    str: 读取到的文件内容，若发生错误则返回空字符串
    """
    
    file_content = ""  # 初始化一个空字符串来存储文件内容
    try:
        # 设定 FTP 登录的用户名和密码
        username = "QPyCode"
        password = "123456"
        
        # 连接到 FTP 服务器
        ftp = FTP(ftp_url)
        
        # 启用被动模式（对于防火墙环境下的连接有帮助）
        ftp.set_pasv(True)
        
        # 使用指定用户名和密码登录
        ftp.login(username, password)
        
        # 切换到目标目录
        ftp.cwd(directory)

        # 定义处理接收到的二进制数据的方法
        def handle_binary_data(data):
            nonlocal file_content # 修改外部的 file_content 变量
            file_content += data.decode('utf-8') # 将二进制数据解码为字符串并追加到 file_content 中

        # 构造 RETR 命令并读取文件
        command = 'RETR {}'.format(filename)
        ftp.retrbinary(command, handle_binary_data) # 使用二进制模式获取文件内容并处理

    except OSError:
        # 如果无法连接到 FTP 服务器，打印错误信息并返回空字符串
        print("无法连接，跳过文件读取。")
        return ""  # 返回空字符串，表示未能成功读取文件
    except Exception as e:
        # 捕获其他异常并打印错误信息，确保程序不崩溃
        print("无法读取文件: {}".format(e))
        return ""  # 返回空字符串，表示读取文件失败
    finally:
        try:
            # 尝试退出 FTP 连接，确保释放资源
            ftp.quit()
        except:
            pass  # 如果退出过程中发生错误，不影响程序执行

    # 返回读取的文件内容
    return file_content



def compare_versions(version1, version2):
    """ 比较两个版本号的大小

    参数:
    version1 (str): 第一个版本号（例如 "1.2.3"）
    version2 (str): 第二个版本号（例如 "1.2.4"）

    返回:
    int: 
        -1 如果 version1 < version2
         1 如果 version1 > version2
         0 如果 version1 == version2
    """
    # 将版本号字符串按点分割，并转换为整数列表
    v1_parts = list(map(int, version1.split(".")))  # 将 version1 分割并转换成整数列表
    v2_parts = list(map(int, version2.split(".")))  # 将 version2 分割并转换成整数列表

    # 比较两个版本号的每一部分
    for v1, v2 in zip(v1_parts, v2_parts):  # 使用 zip 同时迭代 v1_parts 和 v2_parts
        if v1 < v2:
            return -1  # 如果 v1 < v2，则 version1 小于 version2
        elif v1 > v2:
            return 1   # 如果 v1 > v2，则 version1 大于 version2

    # 如果前面的部分相同，比较版本号的长度（即较短的版本号被视为较小）
    if len(v1_parts) < len(v2_parts):
        return -1  # version1 短于 version2，则 version1 小
    elif len(v1_parts) > len(v2_parts):
        return 1   # version1 长于 version2，则 version1 大

    return 0  # 如果前面部分都相同且长度相同，则版本号相等


def update_flag():
    """ 检查本地和服务器版本号，决定是否需要更新代码

    返回:
    bool: 
        - True 如果本地版本较旧，需要更新
        - False 如果本地版本较新或相同，不需要更新
    """
    global update_code_flag  # 声明 update_code_flag 为全局变量，供其他地方使用
    
    # 读取本地版本文件
    text1 = fs.ReadFile("version.txt")  # 假设 fs 是文件系统对象，读取本地版本文件内容
    
    ftp_url = '47.109.46.41'  # FTP 服务器地址
    directory = ''  # 目标目录（为空表示根目录）
    filename = 'version.txt'  # 服务器上版本文件的文件名
    
    # 从 FTP 服务器读取版本文件
    text2 = read_file_from_ftp(ftp_url, directory, filename)
    
    # 如果 FTP 服务器无法读取文件，使用本地版本号
    if text2 == "":
        text2 = text1  # 如果无法获取服务器版本，默认为本地版本
    
    # 可以用来调试打印服务器版本号
    
    # 比较本地版本和服务器版本
    result = compare_versions(text1, text2)

    # 如果本地版本小于服务器版本，表示需要更新
    if result < 0:
        # 本地版本小于服务器版本（调试用）
        update_code_flag = True  # 设置更新标志为 True，表示需要更新代码
    elif result > 0:
        # 本地版本大于服务器版本（调试用）
        update_code_flag = False  # 本地版本较新，不需要更新
    else:
        # printf(text1 + " = " + text2)  # 本地版本等于服务器版本（调试用）
        update_code_flag = False  # 本地版本与服务器版本相同，不需要更新
    
    return update_code_flag  # 返回更新标志

            
def fetch_file_list(ftp_url, directory, username, password):
    """ 从 FTP 服务器获取指定目录下的文件列表（.txt .py .mpy 文件）

    参数:
    ftp_url (str): FTP 服务器的地址
    directory (str): 要查看的目标目录
    username (str): 用于登录 FTP 的用户名
    password (str): 用于登录 FTP 的密码

    返回:
    list: 返回一个包含所有符合条件的文件名的列表（.txt .py .mpy 文件）
    """
    ftp = None  # 初始化 FTP 对象，用于连接和操作 FTP 服务器
    try:
        # 连接到指定的 FTP 服务器
        ftp = FTP(ftp_url)
        
        # 启用 FTP 的被动模式（帮助解决防火墙问题）
        ftp.set_pasv(True)
        
        # 使用提供的用户名和密码进行登录
        ftp.login(username, password)
        
        # 切换到目标目录
        ftp.cwd(directory)
        
        # 获取指定目录下的所有文件和目录名称
        files = ftp.nlst()  # 使用 nlst() 获取目录下的文件和目录列表
        
        # 过滤出扩展名为 .txt 或 .mpy 的文件
        filtered_files = [f for f in files if f.endswith('.txt') or f.endswith('.py') or f.endswith('.mpy')]
        
        # 打印获取到的文件名列表
        print("获取到的文件名: {}".format(", ".join(filtered_files)))
        
        return filtered_files  # 返回过滤后的文件名列表
    except Exception as e:
        # 捕获所有异常并打印错误信息
        print("无法获取文件列表: {}".format(e))
        return []  # 返回空列表表示获取文件列表失败
    finally:
        if ftp:
            # 确保在结束时关闭 FTP 连接，避免资源泄露
            ftp.quit()


def update_code():
    """ 从 FTP 服务器下载文件并执行设备更新操作
    
    该函数从指定的 FTP 服务器获取文件列表，生成下载链接，并通过 FOTA 升级功能下载文件，
    最后设置更新标志并重启设备以完成升级。
    """
    # FTP 服务器的连接信息
    ftp_url = "47.109.46.41"  # FTP 服务器地址
    directory = ""  # 目标目录（根目录）
    username = "QPyCode"  # 登录用户名
    password = "123456"  # 登录密码

    # 从 FTP 服务器获取文件列表
    files = fetch_file_list(ftp_url, directory, username, password)

    # 根据获取的文件列表生成下载链接和目标文件路径
    download_list = [{'url': 'http://47.109.46.41/QPyCode/%s' % (file),  # FTP 文件下载 URL
                      'file_name': '/usr/%s' % file}  # 文件存储路径
                     for file in files]  # 对每个文件生成对应的字典信息

    # 创建一个 FOTA 更新对象
    fota = app_fota.new()  # 假设 app_fota.new() 是用来初始化 FOTA 更新对象的方法
    
    # 执行批量文件下载
    fota.bulk_download(download_list)  # 下载文件列表中的所有文件
    
    # 设置设备的更新标志，标记为需要执行升级
    fota.set_update_flag()  # 设置升级标志，通知设备进行更新

    # 重启设备，完成升级过程
    Power.powerRestart()  # 重启设备以完成更新


