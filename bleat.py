import utime
import _thread

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
        printf("AT线程")
    