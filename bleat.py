import utime
import _thread
import ujson

import sys
# 添加 /usr 目录到模块搜索路径
sys.path.append('/usr')
import um982
import ble


# 创建信号量
at_semaphore = _thread.allocate_semphore(1)


def printf(s):
    print("[ble_at]: " + s)




def init_at():
    # 开启AT线程
    _thread.start_new_thread(AT_thread, ())


def AT_thread():
    while True:
        # 获取信号量
        at_semaphore.acquire()
        
        if "AT\r\n" in ble.at_message:
            ble.ble_send_string("OK\r\n")
        elif "AT+Name=" in ble.at_message:
            # 提取名称部分
            start_index = ble.at_message.index('=') + 1
            end_index = ble.at_message.index('\r\n', start_index)
            name = ble.at_message[start_index:end_index]
            print("Extracted name: " + name)
            ble.uart_ble.write("AT+QBLENAME=" + name + "\r\n")
        elif "AT+JSON=" in ble.at_message:
            data = {'name': 'NiMa', 'age': 30}
            json_str = ujson.dumps(data)
            ble.ble_send_string(json_str)
        elif "AT+{" in ble.at_message:
            try:
                # 提取JSON部分
                json_part = ble.at_message[ble.at_message.index('{'):ble.at_message.index('}') + 1]
                # 解析JSON
                data = ujson.loads(json_part)
                
                # 检查键是否存在
                if "ip" in data and "port" in data and "mount" in data and "accpas" in data:
                    ble.ble_send_string(data["name"] + str(data["age"]))
            except (ValueError, KeyError) as e:
                print("解析JSON时发生错误:", e)
        
        
            
    