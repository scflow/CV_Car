from control import *
import time


if __name__ == '__main__':
    motor.set_speed(5)
    servo.set_angle(60)
    time.sleep(1)
    servo.set_angle(50)
    time.sleep(1)
    servo.set_angle(70)
    time.sleep(1)
    servo.set_angle(60)
    time.sleep(3)
    motor.set_speed(0)
    pigpio_stop()