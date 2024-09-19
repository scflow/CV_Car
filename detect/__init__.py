"""
功能 物块检测、特征匹配
部分常用对象将在本文件中进行初始化，其他代码在import后也可使用初始化后的对象
block   单一颜色物块检测
feature 特征匹配

"""

__version__ = "0.1.0"

from .block import *
from .feature import *

# Block 锥桶
yellow_cone = Block('yellow_cone', 10, 10,
                    np.array([30, 255, 255]), np.array([20, 100, 100]))
blue_cone = Block('blue_cone', 10, 10,
                  np.array([128, 255, 255]), np.array([(90, 0, 0)]))
red_cone = Block('red_cone', 10, 10,
                 np.array([10, 255, 255]), np.array([0, 100, 100]))
# Detect 锥桶
yellow_cone_detect = Detect(yellow_cone, 'yellow_cone_detect', 120, 20)
blue_cone_detect = Detect(blue_cone, 'blue_cone_detect', 120, 20)
red_cone_detect = Detect(red_cone, 'red_cone_detect', 120, 20)

# Block 黄线
yellow_line = Block('yellow_line', 10, 50,
                    np.array([30, 255, 255]), np.array([20, 100, 100]))
# Detect 黄线
yellow_line_detect = Detect(yellow_cone, 'yellow_line_detect', 300, 20)

# Block A4纸
blue_A4 = Block('blue_A4', 15, 15,
                np.array([124, 255, 255]), np.array([100, 43, 46]))
red_A4 = Block('red_A4', 15, 15,
               np.array([179, 255, 255]), np.array([170, 50, 50]))
# Detect A4纸
blue_A4_detect = Detect(blue_A4, 'blue_A4_detect', 120, 20)
red_A4_detect = Detect(red_A4, 'red_A4_detect', 120, 20)

# SIFT 左转
blue_left = Sift('blue_left')
blue_left.detect_and_compute(gray_Red_Left)
# Matcher 左转
blue_left_matcher = Matcher('blue_left_matcher')

# SIFT 右转
blue_right = Sift('blue_right')
blue_right.detect_and_compute(gray_Red_Right)
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
def ZebraCross_find(img):
    # 检测白色范围
    lower_color = np.array([75, 0, 99])  # 颜色下限
    upper_color = np.array([179, 62, 255])  # 颜色上限
    hsv_image = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)  # type: ignore
    mask = cv2.inRange(hsv_image, lower_color, upper_color)
    total_pixels = np.sum(mask == 255)  # 总像素数
    color_percentage = (total_pixels / (hsv_image.shape[0] * hsv_image.shape[1]))
    area_threshold = 0.3
    # 判断面积是否大于阈值
    if color_percentage > area_threshold:
        return True
    else:
        return False


def A4_find(img, A4=red_A4, A4_detect=red_A4_detect):
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_img, A4.color_lower, A4.color_upper)
    kernel = np.ones((40, 40), np.uint8)
    dilated_image = cv2.dilate(mask, kernel, iterations=1)
    contours, _ = cv2.findContours(dilated_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return A4_detect.find_block(contours, return_mode=2)


def line_change(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    Sift_img.detect_and_compute(gray)
    left_bool = blue_left_matcher.knn_match(blue_left.des, Sift_img.des, mode=1)
    right_bool = blue_right_matcher.knn_match(blue_right.des, Sift_img.des, mode=1)
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
    cv2.imshow('mask', mask)
    kernel = np.ones((25, 25), np.uint8)
    dilated_image = cv2.dilate(mask, kernel, iterations=1)
    cv2.imshow('cone_dilated', dilated_image)
    contours, _ = cv2.findContours(dilated_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return Cone_Detect.find_block(contours, return_mode=2)


def AB_recognition(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    Sift_img.detect_and_compute(gray)
    A_bool = blue_A_matcher.knn_match(blue_A.des, Sift_img.des, mode=1)
    B_bool = blue_B_matcher.knn_match(blue_B.des, Sift_img.des, mode=1)
    if A_bool and B_bool:
        return 0
    elif A_bool and not B_bool:
        return 1
    elif B_bool and not A_bool:
        return 2
    elif not A_bool and not B_bool:
        return 0
