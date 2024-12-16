import time
from FPS.utils import FPS
from detect import *
from line.line import *
from loguru_config.config import *
from Audio import play
from undistort import undistort
import control
from pid import pid


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
    # MidLine.upper_x = 160
    # MidLine.lower_x = 160
    if not cap.isOpened():
        logger.error('Cannot open video file')
        exit()
    return time.time(), 0, 0, cap_width, cap_height


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

    # 斑马新检测
    if mode == 1:
        if ZebraCross_find(img):
            control.motor.set_speed(0)
            play.play_audio_blocking()
            time.sleep(2)
            mode += 1

    # 变道识别
    elif mode == 2:
        if anti_shake == 0:
            roi_img = img[280:420, 220:420]
            # cv2.imshow('roi', roi_img)
            if A4_find(roi_img):
                anti_shake = 1
        elif anti_shake == 1:
            # roi_img = img[260:460, 160:480]
            change = line_change(img)
            # cv2.imshow('line_change', img)
            print(f'blue_left_matcher.goodnum: {blue_left_matcher.goodnum} blue_right_matcher.goodnum:{blue_right_matcher.goodnum}')
            if change == 1:
                print(f'Left {blue_left_matcher.goodnum} {blue_right_matcher.goodnum}')
                anti_shake = 0
                mode += 1
                flag = 1
                control.left_line_change()
            elif change == 2:
                print(f'Right {blue_left_matcher.goodnum} {blue_right_matcher.goodnum}')
                anti_shake = 0
                mode += 1
                flag = 2
                control.right_line_change()

    # 锥桶检测
    elif mode == 3:
        if blue_cone_detect.sum < 3:
            if anti_shake == 0:
                roi_img = img[260:440, 240:400]
                # cv2.imshow('cone_roi', roi_img)
                cone_bool = cone_detect(roi_img, blue_cone, blue_cone_detect)
                if cone_bool:
                    logger.info(f'{blue_cone_detect.sum} Cone Has Found')
                    flag = blue_cone_detect.sum
                    anti_shake = 15
                    if flag == 1 or flag == 3:
                        control.left_avoid()
                    if flag == 2:
                        control.right_avoid()
            else:
                anti_shake -= 1
        else:
            anti_shake = 0
            mode += 1

    # A、B停车
    elif mode == 4:
        if anti_shake == 0:
            roi_img = img[360:480, 160:480]
            if A4_find(roi_img):
                anti_shake = 1
        elif anti_shake == 1:
            roi_img = img[320:400, 160:480]
            # cv2.imshow('AB', roi_img)
            parking = AB_recognition(img)
            print(f'{blue_A_matcher.goodnum} {blue_B_matcher.goodnum}')
            if parking == 1:
                flag = 1
                print(f'A {blue_A_matcher.goodnum} {blue_B_matcher.goodnum}')
                control.A_stop()
            elif parking == 2:
                flag = 2
                print(f'B {blue_A_matcher.goodnum} {blue_B_matcher.goodnum}')
                control.B_stop()
            
            if flag == 1 or flag == 2:
                mode += 1
            # print(f'{blue_A_matcher.goodnum} {blue_B_matcher.goodnum}')
    # 黄线检测
    elif mode == 5:
        print(5)
        if yellow_line_detect.sum == 0:
            print(1)
            stop_line(img)
            anti_shake = 5
        elif yellow_line_detect.sum == 1:
            print(2)
            if anti_shake > 0:
                line_stop_count -= 1
            elif line_stop_count == 0:
                stop_line(img)
        elif yellow_line_detect.sum == 2:
            print(3)
            mode += 1        

    return mode, flag


def angle_calc(angle, mode=1):
    """
    角度计算
    @param angle:   以舵机中值为作为0参考
    @return:
    """
    if mode == 1:
        angle = angle + (MidLine.upper_x - 160) * 0.3 + (MidLine.upper_x - MidLine.last_upper_x) * 0.1
    elif mode == 2:
        err = MidLine.upper_x - 160
        if err > 16:
            angle = control.servo.midangle - 20
        elif err > 32:
            angle = control.servo.midangle - 10
        elif err < -16:
            angle = control.servo.midangle + 10
        elif err < -32:
            angle = control.servo.midangle + 20
        else:
            angle = 90
    elif mode == 3:
        angel = control.servo.midangle + servo_pid.cal_output(MidLine.upper_x, 160)
    return angle


if __name__ == '__main__':
    cap = cv2.VideoCapture(0)
    fps = FPS().start()
    servo_pid = pid.PID(upper=8, lower=-8, k=[0.685, 0.001, 0.0005])
    start_time, frame_count, anti_shake, width, height = init()
    find_mode = 2
    find_flag = 0
    angle = 90
    a=0
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_count += 1
            current_time = time.time() - start_time
            if not width == 640:
                frame = cv2.resize(frame, (640, 480))
            if current_time > 3:
                undistort_frame = undistort.undistort(frame)
                if find_mode == 1 or find_mode == 2 or find_mode == 4: 
                    # lane(undistort_frame)
                    try:
                        # angle = control.servo.midangle - servo_pid.cal_output(MidLine.upper_x, 152)
                        print(f'\rangle: {int(angle)}', end=' ')
                    except Exception as e:
                        angle = 90
                        print(e)
                    if current_time > 5:
                        control.servo.set_angle(angle)
                        pass
                if find_mode == 2:
                    find_mode, find_flag = find(frame, find_mode)
                else:
                    find_mode, find_flag = find(undistort_frame, find_mode)
            if current_time > 5:
                if find_mode == 5 or find_mode == 4:
                    control.motor.set_speed(0)
                else:
                    if current_time < 15:
                        control.motor.set_speed(6)
                    elif current_time > 50:
                        control.motor.set_speed(18)
                    else:
                        control.motor.set_speed(6)
            # 识别完毕，结束程序
            if find_mode == 6:
                control.motor.set_speed(0)
                control.pigpio_stop()
                break
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break
            fps.update()
    except KeyboardInterrupt:
        logger.error('Ctrl+C pressed')
        control.pigpio_stop()
    fps.stop()
    cap.release()
    logger.info(f'Elapsed Time: {fps.elapsed():.2f}    Approx. FPS: {fps.fps():.2f}')
    logger.info('Program finished')
