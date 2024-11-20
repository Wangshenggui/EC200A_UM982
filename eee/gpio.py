import machine  # 导入 machine 模块，用于操作硬件

# 定义一个控制GPIO输出的类
class gpio_out:
    def __init__(self, pin_number):
        # 初始化类时，指定一个引脚号，并设置为输出模式
        self.pin = machine.Pin(pin_number, machine.Pin.OUT)
        self.state = False  # 默认状态为关闭（低电平）

    # 设置引脚为高电平（开）
    def set(self):
        self.pin.write(1)  # 设置GPIO引脚输出高电平
        self.state = True  # 更新当前状态为开

    # 设置引脚为低电平（关）
    def reset(self):
        self.pin.write(0)  # 设置GPIO引脚输出低电平
        self.state = False  # 更新当前状态为关

    # 切换引脚状态（开关状态交替）
    def toggle(self):
        if self.state:
            self.reset()  # 如果当前状态是开，则调用 reset() 关闭引脚
        else:
            self.set()  # 如果当前状态是关，则调用 set() 打开引脚
