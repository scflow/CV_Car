import time
from FPS.utils import FPS
from detect import *
from line.line import *
from loguru_config.config import *
from playsound import playsound


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
    MidLine.upper_x = 160
    MidLine.lower_x = 160
    if not cap.isOpened():
        logger.error('Cannot open video file')
        exit()
    return time.time(), 0, 0, cap_width, cap_height


def lane(img):
    """
    跑道检测
    """
    resize_img = cv2.resize(img, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_CUBIC)
    lane_img = show_lane(resize_img, 2)
    cv2.imshow('lane_img', lane_img)
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
            playsound('Audio/test.mp3')
            mode += 1

    # 变道识别
    elif mode == 2:
        if anti_shake == 0:
            roi_img = img[320:480, 80:560]
            if A4_find(roi_img):
                anti_shake = 1
        elif anti_shake == 1:
            roi_img = img[320:480, 80:560]
            cv2.imshow('roi_img', roi_img)
            change = line_change(roi_img)
            if change == 1:
                print(f'Left {blue_left_matcher.goodnum} {blue_right_matcher.goodnum}')
                anti_shake = 0
                mode += 1
                flag = 1
            elif change == 2:
                print(f'Right {blue_left_matcher.goodnum} {blue_right_matcher.goodnum}')
                anti_shake = 0
                mode += 1
                flag = 2

    # 锥桶检测
    elif mode == 3:
        if yellow_cone_detect.sum < 3:
            if anti_shake == 0:
                cone_bool = cone_detect(img, yellow_cone, yellow_cone_detect)
                if cone_bool:
                    logger.info(f'{yellow_cone_detect.sum} Cone Has Found')
                    flag = yellow_cone_detect.sum
                    anti_shake = 15
            else:
                anti_shake -= 1
        else:
            anti_shake = 0
            mode += 1

    # A、B停车
    elif mode == 4:
        if anti_shake == 0:
            roi_img = img[320:480, 80:560]
            if A4_find(roi_img):
                anti_shake = 1
        elif anti_shake == 1:
            parking = AB_recognition(img)
            if parking == 1:
                flag = 1
                print(f'Left  A {blue_A_matcher.goodnum} {blue_B_matcher.goodnum}')
            elif parking == 2:
                flag = 2
                print(f'Right B {blue_A_matcher.goodnum} {blue_B_matcher.goodnum}')

    return img, mode, flag


def angle_calc(angle, mode, flag):
    """
    角度计算
    @param angle:   以舵机中值为作为0参考
    @param mode:    find函数mode
    @param flag:    find函数flag
    @return:
    """
    angle = angle + (MidLine.upper_x - width // 4) * 0.0005
    if mode == 2:
        if flag == 1:
            angle += 5
            time.sleep(1)
            angle -= 5
            time.sleep(1)
        elif flag == 2:
            angle -= 5
            time.sleep(1)
            angle += 5
            time.sleep(1)
    elif mode == 3:
        if flag == 1 or flag == 3:
            angle += 2
            time.sleep(0.5)
            angle -= 2
            time.sleep(0.5)
        elif flag == 2:
            angle -= 2
            time.sleep(0.5)
            angle += 2
            time.sleep(0.5)
    elif mode == 4:
        if flag == 1:
            angle += 5
            time.sleep(1)
            angle -= 5
            time.sleep(1)
        elif flag == 2:
            angle -= 5
            time.sleep(1)
            angle += 5
            time.sleep(1)

    return angle


if __name__ == '__main__':
    cap = cv2.VideoCapture('Video/pgv7.mp4')
    fps = FPS().start()
    start_time, frame_count, anti_shake, width, height = init()
    find_mode = 1
    find_flag = 0
    angle = 0
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_count += 1
            if not width == 640:
                frame = cv2.resize(frame, (640, 480))
            resize_frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_CUBIC)
            lane(frame)
            _, find_mode, find_flag = find(frame, find_mode)
            angle = angle_calc(angle, find_mode, find_flag)
            print(f'\rDrop Rate: {MidLine.lose_count / frame_count * 100:.2f}%  '
                  f'error_num: {MidLine.error_num} {MidLine.upper_x - width // 4} '
                  f'angle: {angle}', end=' ')
            if find_mode == 5:
                break
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            fps.update()
    except KeyboardInterrupt:
        logger.error('Ctrl+C pressed')
    fps.stop()
    cap.release()
    logger.info(f'Elapsed Time: {fps.elapsed():.2f}    Approx. FPS: {fps.fps():.2f}')
    logger.info('Program finished')
