import machine



class gpio_out:
    def __init__(self, pin_number):
        self.pin = machine.Pin(pin_number, machine.Pin.OUT)
        self.state = False  # 初始状态为关闭

    def set(self):
        self.pin.write(1)
        self.state = True

    def reset(self):
        self.pin.write(0)
        self.state = False

    def toggle(self):
        if self.state:
            self.reset()
        else:
            self.set()
            
            
            