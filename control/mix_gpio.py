from control import *
import time


if __name__ == '__main__':
    # motor.set_speed(9)
    servo.set_angle(60)
    time.sleep(1)
    print(1)
    servo.set_angle(47)
    time.sleep(0.8)
    print(2)
    servo.set_angle(90)
    time.sleep(1)
    servo.set_angle(47)
    time.sleep(1)
    servo.set_angle(60)
    time.sleep(1)
    motor.set_speed(0)
    pigpio_stop()