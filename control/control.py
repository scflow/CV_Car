import pigpio
import os


class Motor:
    def __init__(self):
        self.pi = pigpio.pi()
        self.name = 'Motor'
        self.pin = 13
        self.pi.set_mode(self.pin, pigpio.OUTPUT)
        self.pi.set_PWM_frequency(self.pin, 50)
        self.pi.set_PWM_range(self.pin, 40000)

    def set_speed(self, speed):
        """
        speed范围为0-100, speed会计算并转为对应pwm占空比值
        :speed 0 为停止， 6 电机即可启动
        """
        pwm_dutycycle = (100 - speed) * 100
        self.pi.set_PWM_dutycycle(self.pin, pwm_dutycycle)


class Servo:
    def __init__(self, name, pin, frequency=50, pwm_range=1000):
        self.pi = pigpio.pi()
        self.name = name
        self.pin = pin
        self.range = pwm_range
        self.pi.set_mode(self.pin, pigpio.OUTPUT)
        self.pi.set_PWM_frequency(self.pin, frequency)
        self.pi.set_PWM_range(self.pin, self.range)

    def set_angle(self, angle):
        self.pi.set_PWM_dutycycle(self.pin, angleToDutyCycle(angle) * self.range / 100)

def angleToDutyCycle(angle):
    return (2.5 + (angle / 180.0) * 10) * 1


def pigpio_start():
    os.system(open_io)
    os.system(close_rc)


def pigpio_stop():
    os.system(close_io)


close_rc = "sudo systemctl stop network-rc.service"
open_io = "sudo pigpiod"
close_io = "sudo killall pigpiod"

motor = Motor()
servo = Servo('servo', 12)
gimbal_x = Servo('gimbal_x', 22)
gimbal_y = Servo('gimbal_y', 23)
