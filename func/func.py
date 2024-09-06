import time
from playsound import playsound
from detect import *
from line.line import *
from loguru_config.config import *

setlog()


def init(cap):
    """
    部分设置初始化
    """
    setlog()
    cap_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    LeftLine.set_img(cap_height // 2, cap_width // 2)
    RightLine.set_img(cap_height // 2, cap_width // 2)
    MidLine.set_img(cap_height // 2, cap_width // 2)
    if not cap.isOpened():
        logger.error('Cannot open video file')
        exit()
    return time.time(), 0, 0, cap_width, cap_height


def lane(img):
    """
    跑道检测
    """
    resize_img = cv2.resize(img, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_CUBIC)
    lane_img = show_lane(resize_img, 1)
    return lane_img


def find(img, mode):
    """
    物块检测、特征匹配
    :param img:     传入图片
    :param mode:    检测模式
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
            roi_img = img[150:600, 200:700]
            if A4_find(roi_img):
                anti_shake = 1
        elif anti_shake == 1:
            roi_img = img[400:600, 450:700]
            cv2.imshow('roi_img', roi_img)
            change = line_change(roi_img)
            if change == 1:
                print(f'Left {blue_left_matcher.goodnum} {blue_right_matcher.goodnum}')
                anti_shake = 0
                mode += 1
            elif change == 2:
                print(f'Right {blue_left_matcher.goodnum} {blue_right_matcher.goodnum}')
                anti_shake = 0
                mode += 1

    # 锥桶检测
    elif mode == 3:
        if yellow_cone_detect.sum < 3:
            if anti_shake == 0:
                cone_bool = cone_detect(img, yellow_cone, yellow_cone_detect)
                if cone_bool:
                    logger.info(f'{yellow_cone_detect.sum} Cone Has Found')
                    anti_shake = 15
            else:
                anti_shake -= 1
        else:
            anti_shake = 0
            mode += 1

    # A、B停车
    elif mode == 4:
        if anti_shake == 0:
            if A4_find(img):
                anti_shake = 1
        elif anti_shake == 1:
            parking = AB_recognition(img)
            if parking == 1:
                print(f'Left  A {blue_A_matcher.goodnum} {blue_B_matcher.goodnum}')
            elif parking == 2:
                print(f'Right B {blue_A_matcher.goodnum} {blue_B_matcher.goodnum}')

    return img, mode


def angle_calc():
    return None


def GUI(img):
    return img
