"""
功能 物块检测、特征匹配
部分常用对象将在本文件中进行初始化，其他代码在import后也可使用初始化后的对象
block   单一颜色物块检测
feature 特征匹配

"""

__version__ = "0.1.1"

from .block import *
from .feature import *

# Block 锥桶
yellow_cone = Block('yellow_cone', 10, 10,
                    np.array([30, 255, 255]), np.array([20, 100, 100]))
blue_cone = Block('blue_cone', 6, 6,
                  np.array([108, 255, 255]), np.array([(100, 127, 51)]))
red_cone = Block('red_cone', 10, 10,
                 np.array([10, 255, 255]), np.array([0, 100, 100]))
# Detect 锥桶
yellow_cone_detect = Detect(yellow_cone, 'yellow_cone_detect', 90, 15)
blue_cone_detect = Detect(blue_cone, 'blue_cone_detect', 60, 15)
red_cone_detect = Detect(red_cone, 'red_cone_detect', 85, 15)

# Block 黄线
yellow_line = Block('yellow_line', 10, 50,
                    np.array([30, 255, 255]), np.array([10, 80, 100]))
# Detect 黄线
yellow_line_detect = Detect(yellow_cone, 'yellow_line_detect', 300, 20)


# Block A4纸
blue_A4 = Block('blue_A4', 10, 10,
                np.array([108, 255, 255]), np.array([(100, 127, 51)]))
blue_A4 = Block('blue_A4', 10, 10,
                np.array([100, 95, 170]), np.array([140, 255, 255]))

red_A4 = Block('red_A4', 15, 15,
               np.array([179, 255, 255]), np.array([170, 50, 50]))
# Detect A4纸
blue_A4_detect = Detect(blue_A4, 'blue_A4_detect', 67, 20)
red_A4_detect = Detect(red_A4, 'red_A4_detect', 90, 20)

# SIFT 左转
blue_left = Sift('blue_left')
blue_left.detect_and_compute(gray_Turn_Left)
# Matcher 左转
blue_left_matcher = Matcher('blue_left_matcher')

# SIFT 右转
blue_right = Sift('blue_right')
blue_right.detect_and_compute(gray_Turn_Right)
# Matcher 右转
blue_right_matcher = Matcher('blue_right_matcher')

# SIFT A
blue_A = Sift('blue_A')
blue_A.detect_and_compute(gray_Blue_A)
# Matcher A
blue_A_matcher = Matcher('blue_A')

# SIFT B
blue_B = Sift('blue_B')
blue_B.detect_and_compute(gray_Blue_B)
# Matcher B
blue_B_matcher = Matcher('blue_B_matcher')

# SIFT img
Sift_img = Sift('Sift_img')


# 检测函数以及实现
def ZebraCross_find(img, area_threshold=0.3):
    # 检测白色范围
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 195, 255,cv2.THRESH_BINARY)
    roi_img  =  thresh[250:350, 120:520]
    resize_img = cv2.resize(roi_img,(0,0),fx=0.5,fy=0.5)
    # mask = cv2.inRange(resize_img, lower_color, upper_color)
    total_pixels = np.sum(resize_img == 255)  # 总像素数
    color_percentage = (total_pixels / (resize_img.shape[0] * resize_img.shape[1])) * 100
    print(f'color_percentage: {color_percentage}')
    # 判断面积是否大于阈值
    if color_percentage > area_threshold:
        return True
    else:   
        return False


def A4_find(img, A4=blue_A4, A4_detect=blue_A4_detect):
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_img, A4.color_lower, A4.color_upper)
    kernel = np.ones((19, 19), np.uint8)
    dilated_image = cv2.dilate(mask, kernel, iterations=1)
    contours, _ = cv2.findContours(dilated_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cv2.imshow('dilated_image', dilated_image)
    return A4_detect.find_block(contours, return_mode=2)


def line_change(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    adjusted_image = cv2.convertScaleAbs(gray, alpha=1, beta=0)
    # cv2.imshow('line_change_gray', adjusted_image)
    Sift_img.detect_and_compute(adjusted_image)
    try:
        left_bool = blue_left_matcher.knn_match(blue_left.des, Sift_img.des, num=8, mode=1)
        right_bool = blue_right_matcher.knn_match(blue_right.des, Sift_img.des, num=8, mode=1)
    except Exception as e:
        left_bool = 0
        right_bool = 0
    if left_bool and right_bool:
        return 0
    elif left_bool and not right_bool:
        return 1
    elif right_bool and not left_bool:
        return 2
    elif not left_bool and not right_bool:
        return 0


def cone_detect(img, Cone=blue_cone, Cone_Detect=blue_cone_detect):
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_img, Cone.color_lower, Cone.color_upper)
    # cv2.imshow('mask', mask)
    kernel = np.ones((19, 19), np.uint8)
    dilated_image = cv2.dilate(mask, kernel, iterations=1)
    # cv2.imshow('cone_dilated', dilated_image)
    contours, _ = cv2.findContours(dilated_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return Cone_Detect.find_block(contours, return_mode=2)


def AB_recognition(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # adjusted_image = cv2.convertScaleAbs(gray, alpha=1, beta=-30)
    Sift_img.detect_and_compute(gray)
    A_bool = blue_A_matcher.knn_match(blue_A.des, Sift_img.des, num=6, mode=1)
    B_bool = blue_B_matcher.knn_match(blue_B.des, Sift_img.des, num=6, mode=1)
    if A_bool and B_bool:
        return 0
    elif A_bool and not B_bool:
        return 1
    elif B_bool and not A_bool:
        return 2
    elif not A_bool and not B_bool:
        return 0


def stop_line(img):
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    yellow_mask = cv2.inRange(hsv_img, yellow_line.color_lower, yellow_line.color_upper)
    # cv2.imshow('mask', yellow_mask)
    vline = cv2.getStructuringElement(cv2.MORPH_RECT, (1, int(yellow_mask.shape[0] / 16)))
    vertical_lines = cv2.morphologyEx(yellow_mask, cv2.MORPH_OPEN, vline)
    mask_without_vlines = cv2.subtract(yellow_mask, vertical_lines)
    hline = cv2.getStructuringElement(cv2.MORPH_RECT, (int(yellow_mask.shape[1] / 16), 1))
    horizontal_lines = cv2.morphologyEx(mask_without_vlines, cv2.MORPH_OPEN, hline)
    kernel = np.ones((25, 25), np.uint8)
    erode_image = cv2.dilate(horizontal_lines, kernel, iterations=1)
    # cv2.imshow('yellow_lind', erode_image)
    contours, hierarchy = cv2.findContours(erode_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    yellow_line_detect.find_block(contours, print_mode=0, return_mode=0)
