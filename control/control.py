import pigpio
import time
import os


class Motor:
    def __init__(self):
        self.pi = pigpio.pi()
        self.name = 'Motor'
        self.pin = 13
        self.pi.set_mode(self.pin, pigpio.OUTPUT)
        self.pi.set_PWM_frequency(self.pin, 200)
        self.pi.set_PWM_range(self.pin, 40000)

    def set_speed(self, speed):
        """
        speed范围为0-100, speed会计算并转为对应pwm占空比值
        :speed 0 为停止， 6 电机即可启动
        """
        pwm_dutycycle = (100 - speed) * 100
        self.pi.set_PWM_dutycycle(self.pin, pwm_dutycycle)


class Servo:
    def __init__(self, name, pin, frequency=50, pwm_range=1000, angle_max=110, angle_min=70):
        self.pi = pigpio.pi()
        self.name = name
        self.pin = pin
        self.range = pwm_range
        self.angle_max = angle_max
        self.angle_min = angle_min
        self.pi.set_mode(self.pin, pigpio.OUTPUT)
        self.pi.set_PWM_frequency(self.pin, frequency)
        self.pi.set_PWM_range(self.pin, self.range)
        self.pi.set_PWM_dutycycle(self.pin, angleToDutyCycle(80) * self.range / 100)

    def set_angle(self, angle):
        if angle < self.angle_min:
            angle = self.angle_min
        elif angle > self.angle_max:
            angle = self.angle_max
        self.pi.set_PWM_dutycycle(self.pin, angleToDutyCycle(angle) * self.range / 100)

def angleToDutyCycle(angle):
    return 2.5 + (angle / 180.0) * 10


def pigpio_start():
    os.system(open_io)
    os.system(close_rc)


def pigpio_stop():
    os.system(close_io)
    os.system(open_io)


close_rc = "sudo systemctl stop network-rc.service"
open_io = "sudo pigpiod"
close_io = "sudo killall pigpiod"

motor = Motor()
servo = Servo('servo', 22, angle_max=95, angle_min=45)
gimbal_x = Servo('gimbal_x', 16)
gimbal_y = Servo('gimbal_y', 23)
motor.set_speed(0)
time.sleep(1)
print('预处理完成')
