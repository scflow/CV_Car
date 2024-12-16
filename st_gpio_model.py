import time
from FPS.utils import FPS
from detect import *
from line.line import *
from loguru_config.config import *
from Audio import play
from undistort import undistort
import control
from filter import *
from model import detector
from datetime import datetime
import os

def init():
    """
    部分设置初始化
    """
    setlog()
    cap_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    lane_resize = 2
    LeftLine.set_img(cap_height // lane_resize, cap_width // lane_resize)
    RightLine.set_img(cap_height // lane_resize, cap_width // lane_resize)
    MidLine.set_img(cap_height // lane_resize, cap_width // lane_resize)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'data/{timestamp}'
    if not cap.isOpened():
        logger.error('Cannot open Video File or Camera')
        exit()
    return time.time(), 0, 0, cap_width, cap_height, filename


def lane(img):
    """
    跑道检测
    """
    resize_img = cv2.resize(img, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_CUBIC)
    lane_img = show_lane(resize_img, mode=2)
    # cv2.imshow('lane_img', lane_img)
    return lane_img


def find(img, mode, flag=0):
    """
    物块检测、特征匹配
    :param img:     传入图片
    :param mode:    检测模式
    :param flag:    偏差
    """
    global anti_shake
    global filename
    global current_time
    global except_des
    # 斑马新检测
    if mode == 1:
        if ZebraCross_find(img, area_threshold=2.8):
            control.motor.set_speed(8)
            control.servo.set_angle(control.servo.midangle + 15)
            time.sleep(1.2)
            control.servo.set_angle(control.servo.midangle - 15)
            time.sleep(0.4)
            control.motor.set_speed(0)
            play.play_audio_blocking(audio_file='Audio/stop.mp3')
            time.sleep(1)
            except_des = 152
            mode += 1

    # 变道识别
    elif mode == 2:
        if anti_shake == 0:
            roi_img = img[280:420, 220:420]
            cv2.imshow('roi', roi_img)
            if A4_find(roi_img):
                anti_shake = 1
        elif anti_shake == 1:
            roi_img = img[280:460, 220:420]
            start = time.time()
            # cv2.imshow('img', img)
            target_cls_indices = [0, 1]
            cls_found = detector.detection(roi_img, target_cls_indices)
            end = time.time()
            print(f'time:{end - start}')
            if cls_found[0] and not cls_found[1]:
                anti_shake = 0
                mode += 1
                flag = 1
                logger.info(f'Trun Left')
                control.motor.set_speed(10)
                control.left_line_change()
                cv2.imwrite(f'{filename}/line_change_left.jpg', img)
            elif cls_found[1] and not cls_found[0]:
                anti_shake = 0
                mode += 1
                flag = 2
                logger.info(f'Trun Right')
                control.motor.set_speed(10)
                control.right_line_change()
                cv2.imwrite(f'{filename}/line_change_left.jpg', img)

    # 锥桶检测
    elif mode == 3:
        if blue_cone_detect.sum < 3:
            if 0 == blue_cone_detect.sum:
                except_des = 152     
            if anti_shake == 0:
                roi_img = img[280:440, 200:440]
                cv2.imshow('cone_roi', roi_img)
                cone_bool = cone_detect(roi_img, blue_cone, blue_cone_detect)
                if cone_bool:
                    control.servo.midangle = 90
                    logger.info(f'{blue_cone_detect.sum} Cone Has Found')
                    flag = blue_cone_detect.sum
                    anti_shake = 10
                    cv2.imwrite(f'{filename}/cone_{flag}.jpg', roi_img)
                    if flag == 1:
                        except_des = 140
                    if flag == 2:
                        except_des = 164
                    elif flag == 3:
                        except_des = 152
            else:
                anti_shake -= 1
        else:
            anti_shake = 0
            mode += 1

    # A、B停车
    elif mode == 4:
        if anti_shake == 0:
            roi_img = img[240:480, 120:520]
            if A4_find(roi_img):
                anti_shake = 1  
                control.motor.set_speed(0)           
                cv2.imwrite(f'{filename}/B_A4.jpg', roi_img)
        elif anti_shake == 1:
            start = time.time()
            target_cls_indices = [2, 3]
            detector.thresh = 0.65
            cls_found = detector.detection(img, target_cls_indices)
            end = time.time()
            print(f'time:{end - start}')
            if cls_found[3]:
                flag = 2
                logger.info(f'Stop B')
                control.B_stop()
                cv2.imwrite(f'{filename}/stop_B.jpg', img)
            else:
                flag = 1
                logger.info(f'Stop A')
                control.A_stop()
                cv2.imwrite(f'{filename}/stop_A.jpg', img)
            if cls_found[2]:
                flag = 1
                logger.info(f'Stop A')
                control.B_stop()
                cv2.imwrite(f'{filename}/stop_A.jpg', img)
            else:
                flag = 1
                logger.info(f'Stop B')
                control.B_stop()
                cv2.imwrite(f'{filename}/stop_B.jpg', img)
            if flag == 1 or flag == 2:
                mode += 1
    return mode, flag


def calculate_speed(current_time, start_time, end_time, start_speed, end_speed):
    if current_time < start_time:
        return start_speed
    elif current_time >= end_time:
        return end_speed
    else:
        # 线性插值
        t = (current_time - start_time) / (end_time - start_time)
        return start_speed + t * (end_speed - start_speed)


def get_target_speed(find_mode, current_time, time4):
    """获取目标速度
    Args:
        find_mode: 当前模式
        current_time: 当前时间
    Returns:
        speed: 目标速度值
    """
    global except_des
    # 5-8秒为启动阶段,速度从0线性增加到目标速度
    # if 3 < current_time < 6:
    #     return calculate_speed(current_time, 3, 6, 0, 30)
        
    # 变道和停车模式用较低速度
    if find_mode == 2:
        return 10
    
    if find_mode == 4 and anti_shake == 1:
        return 10
    
    if find_mode == 4 and anti_shake == 0:
        return 30
        # if current_time - time4 < 5:
        #     return calculate_speed(current_time, time4, time4 + 3, 10, 14)
        # elif current_time - time4 < 7:
        #     return calculate_speed(current_time, time4 + 5, time4 + 7, 14, 10)
        
    # 模式1的速度控制
    if find_mode == 1:
        if current_time < 42:
        #     return 15
        # elif current_time < 40:
            return calculate_speed(current_time, 4, 10, 0, 30)
        elif current_time < 53:
            except_des = 149
            return calculate_speed(current_time, 50, 53, 30, 6)
        elif current_time < 57:
            return calculate_speed(current_time, 53, 57, 6, 0)
        # elif current_time < 69:
        #     return calculate_speed(current_time, 64, 67, 10, 0)
        else:
            return 6
    if find_mode == 3:
        return 30
    # 其他模式默认速度
    return 10


if __name__ == '__main__':
    cap = cv2.VideoCapture(0)
    fps = FPS().start()
    servo_pid = pid.PID(upper=8, lower=-8, k=[0.75, 0.01, 0.05])
    kf = kalmanfilter.KalmanFilter()
    start_time, frame_count, anti_shake, width, height, filename = init()
    os.mkdir(f'{filename}')
    find_mode = 1
    find_flag = 0
    time4 = 0
    angle = 90
    filtered_angle = 90
    time_points = []
    angle_data = []
    speed_data = []
    except_des = 152
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break  
            last_mode = find_mode
            frame_count += 1
            current_time = time.time() - start_time
            if frame.shape[1] != 640:
                frame = cv2.resize(frame, (640, 480))
            if current_time > 3:
                # if find_mode in {1, 3, 4}:
                frame = undistort.undistort(frame)
                lane(frame)
                try:
                    angle = control.servo.midangle - servo_pid.cal_output(MidLine.upper_x, except_des)
                    # kf.predict()
                    # kf.update(angle)
                    # filtered_angle = kf.x[0][0]
                    filtered_angle = angle
                    print(f'angle: {int(filtered_angle)}, speed: {control.motor.speed} mode:{find_mode} MidLine.upper_x:{MidLine.upper_x} current_time:{current_time}')
                except Exception as e:
                    angle = 90
                    print(e)
                if current_time > 4:
                    control.servo.set_angle(filtered_angle)
                    pass       
                if find_mode == 1:
                    control.servo.midangle = 83
                    # if current_time > 60:
                    find_mode, find_flag = find(frame, find_mode)
                else:
                    control.servo.midangle = 83
                    find_mode, find_flag = find(frame, find_mode)
                if last_mode == 3 and find_mode == 4:
                    time4 = time.time() - start_time
                speed = get_target_speed(find_mode, current_time, time4)
                control.motor.set_speed(speed)
            # plt_recoder(int(filtered_angle), control.motor.speed, find_mode, find_flag, fps.fps())
            if find_mode == 5:
                control.motor.set_speed(0)
                control.pigpio_stop()
                # plt_recoder.save_plot()
                # plt_recoder.save_data()
                break
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            fps.update()
    except KeyboardInterrupt:
        logger.error('Ctrl+C pressed')
        control.pigpio_stop()
    fps.stop()
    cap.release()
    logger.info(f'Elapsed Time: {fps.elapsed():.2f}    Approx. FPS: {fps.fps():.2f}')
    logger.info('Program finished')
