import pigpio
import time
import os
import pygame
import math
from Audio import play


class Motor:
    def __init__(self, pin=13):
        self.pi = pigpio.pi()
        self.name = 'Motor'
        self.pin = pin
        self.pi.set_mode(self.pin, pigpio.OUTPUT)
        self.pi.set_PWM_frequency(self.pin, 200)
        self.pi.set_PWM_range(self.pin, 40000)
        self.speed = 0

    def set_speed(self, speed):
        """
        speed范围为0-100, speed会计算并转为对应pwm占空比值
        :speed 0 为停止
        """
        self.speed = speed
        pwm_dutycycle = (100 - speed) * 100
        self.pi.set_PWM_dutycycle(self.pin, pwm_dutycycle)
        
    def calculate_speed(current_time, start_time, end_time, start_speed, end_speed):
        if current_time < start_time:
            return start_speed
        elif current_time >= end_time:
            return end_speed
        else:
            # 线性插值
            t = (current_time - start_time) / (end_time - start_time)
            return start_speed + t * (end_speed - start_speed)


class Servo:
    def __init__(self, name, pin, frequency=50, pwm_range=1000, angle_max=110, angle_min=70):
        self.pi = pigpio.pi()
        self.name = name
        self.pin = pin
        self.range = pwm_range
        self.pi.set_PWM_frequency(self.pin, frequency)
        self.pi.set_PWM_range(self.pin, self.range)
        self.pi.set_mode(self.pin, pigpio.OUTPUT)
        self.angle_max = angle_max
        self.angle_min = angle_min
        self.angle = None

    def set_angle(self, angle):
        if angle > self.angle_max:
            angle = self.angle_max
        elif angle < self.angle_min:
            angle = self.angle_min
        self.angle = angle
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

pigpio_start()
play.play_audio_blocking(audio_file='Audio/doorbell.mp3')
motor = Motor(pin=13)
motor.set_speed(0)
servo = Servo('servo', 22, angle_max=110, angle_min=70)
servo.midangle = 83
servo.set_angle(servo.midangle)
gimbal_x = Servo('gimbal_x', 16)
gimbal_x.set_angle(87)
gimbal_y = Servo('gimbal_y', 23)
gimbal_y.set_angle(98)


# def left_avoid():
#     # 前半段时间较短
#     rise_duration = 0.16  
#     # 后半段时间较长
#     fall_duration = 0.16
#     # 最大值停留时间
#     hold_duration = 0.7
    
#     steps = 50
#     max_angle = 14
    
#     # 上升阶段
#     rise_step_time = rise_duration / steps
#     for i in range(steps):
#         t = i / steps
#         angle = max_angle * math.sin(math.pi * t / 2)  # 0 到 max_angle
#         servo.set_angle(servo.midangle + angle)
#         time.sleep(rise_step_time)
    
#     # 最大值停留
#     servo.set_angle(servo.midangle + max_angle)
#     time.sleep(hold_duration)
    
#     # 下降阶段
#     fall_step_time = fall_duration / steps
#     for i in range(steps):
#         t = i / steps
#         angle = max_angle * math.cos(math.pi * t / 2)  # max_angle 到 0
#         servo.set_angle(servo.midangle - angle)
#         time.sleep(fall_step_time)
#         # 最大值停留
#     servo.set_angle(servo.midangle - max_angle)
#     time.sleep(0.3)
#     servo.set_angle(servo.midangle + 10)
#     time.sleep(0.4)
#     servo.set_angle(servo.midangle - 4)
#     time.sleep(0.1)
#     servo.set_angle(servo.midangle - 8)
#     time.sleep(0.2)
#     servo.set_angle(servo.midangle - 12)
#     time.sleep(0.3)
#     servo.set_angle(servo.midangle - 14)
#     time.sleep(0.1)
#     # servo.set_angle(servo.midangle - 10)
#     # time.sleep(0.2)
#     servo.set_angle(servo.midangle)


def left_avoid():
    servo.set_angle(servo.midangle)
    time.sleep(0.04)
    rise_duration = 0.1  # 上升段时间
    fall_duration = 0.4  # 下降段时间较长
    final_rise_duration = 0.1  # 最后上升段时间
    hold_duration = 0.2  # 极值点停留时间
    
    steps = 5
    max_angle = 14
    
    # 上升阶段 (0 到 max_angle)
    rise_step_time = rise_duration / steps
    for i in range(steps):
        t = i / steps
        angle = max_angle * math.sin(math.pi * t)
        servo.set_angle(servo.midangle + angle)
        time.sleep(rise_step_time)
        # print(servo.angle)
    
    # 正极值停留
    servo.set_angle(servo.midangle + max_angle)
    # print(servo.angle)
    time.sleep(hold_duration + 0.2)
    
    # 下降阶段 (max_angle 到 -max_angle)
    fall_step_time = fall_duration / steps
    for i in range(steps):
        t = i / steps
        angle = max_angle * math.sin(math.pi * (1 + t))
        servo.set_angle(servo.midangle + angle)
        time.sleep(fall_step_time)
        # print(servo.angle)
    
    # 负极值停留
    servo.set_angle(servo.midangle - max_angle)
    time.sleep(hold_duration + 1)
    # print(servo.angle)
    
    # 最终上升阶段 (-max_angle 到 0)
    final_rise_step_time = final_rise_duration / steps
    for i in range(steps):
        t = i / steps
        angle = -max_angle * math.cos(math.pi * t / 2)  # 使用余弦函数实现平滑过渡
        servo.set_angle(servo.midangle + angle)
        time.sleep(final_rise_step_time)
        # print(servo.angle)
    rise_step_time = rise_duration / steps + 0.01
    for i in range(steps):
        t = i / steps
        angle = max_angle * math.sin(math.pi * t)
        servo.set_angle(servo.midangle + angle)
        time.sleep(rise_step_time)

def right_avoid():
    servo.set_angle(servo.midangle)
    time.sleep(0.01)
    rise_duration = 0.1  # 上升段时间
    fall_duration = 0.2  # 下降段时间较长
    final_rise_duration = 0.1  # 最后上升段时间
    hold_duration = 0.65  # 极值点停留时间
    
    steps = 10
    max_angle = 14
    
    # 上升阶段 (0 到 max_angle)
    rise_step_time = rise_duration / steps
    for i in range(steps):
        t = i / steps
        angle = max_angle * math.sin(math.pi * t)
        servo.set_angle(servo.midangle - angle)
        time.sleep(rise_step_time)
    #     print(servo.angle)
    # print()
    # 正极值停留
    servo.set_angle(servo.midangle - max_angle)
    time.sleep(hold_duration - 0.1)
    # print(servo.angle)
    # print()
    # 下降阶段 (max_angle 到 -max_angle)
    fall_step_time = fall_duration / steps
    for i in range(steps):
        t = i / steps
        angle = -max_angle * math.sin(math.pi * (1 + t))
        servo.set_angle(servo.midangle + angle)
        time.sleep(fall_step_time)
        # print(servo.angle)
    # print()
    # 负极值停留
    servo.set_angle(servo.midangle + max_angle)
    time.sleep(hold_duration - 0.3)
    print(servo.angle)
    # print()
    # 最终上升阶段 (-max_angle 到 0)
    final_rise_step_time = final_rise_duration / steps
    for i in range(steps):
        t = i / steps
        angle = max_angle * math.cos(math.pi * t / 2)  # 使用余弦函数实现平滑过渡
        servo.set_angle(servo.midangle + angle)
        time.sleep(final_rise_step_time)
        rise_step_time = rise_duration / steps
    rise_step_time = rise_duration / steps
    for i in range(steps):
        t = i / steps
        angle = max_angle * math.sin(math.pi * t)
        servo.set_angle(servo.midangle - angle)
        time.sleep(rise_step_time)

def left_line_change():
    servo.set_angle(servo.midangle + 13)
    time.sleep(2.0)
    servo.set_angle(servo.midangle - 13)
    time.sleep(0.5)
    servo.set_angle(servo.midangle)

def right_line_change():
    servo.set_angle(servo.midangle - 10)
    time.sleep(1.5)
    servo.set_angle(servo.midangle + 10)
    time.sleep(2.0)
    servo.set_angle(servo.midangle)

def A_stop():
    servo.set_angle(servo.midangle + 10)
    time.sleep(0.8)
    servo.set_angle(servo.midangle)

def B_stop():
    servo.set_angle(servo.midangle - 10)
    time.sleep(0.6)
    servo.set_angle(servo.midangle)
