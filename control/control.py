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

    def speed(self, speed):
        self.pi.set_PWM_dutycycle(self.pin, speed)


class Servo:
    def __init__(self, name, pin):
        self.pi = pigpio.pi()
        self.name = name
        self.pin = pin
        self.pi.set_mode(self.pin, pigpio.OUTPUT)
        self.pi.set_PWM_frequency(self.pin, 200)
        self.pi.set_PWM_range(self.pin, 40000)

    def angle(self, angle):
        self.pi.set_PWM_dutycycle(self.pin, angleToDutyCycle(angle))


def angleToDutyCycle(angle):
    return 2.5 + (angle / 180.0) * 10


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
gimbal_x = Servo('gimbal_x', 12)
gimbal_y = Servo('gimbal_y', 12)
