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
                  np.array([124, 255, 255]), np.array([100, 43, 46]))
# Detect 锥桶
yellow_cone_detect = Detect(yellow_cone, 'yellow_cone_detect', 400, 40)
blue_cone_detect = Detect(blue_cone, 'blue_cone_detect', 370, 20)

# Block 黄线
yellow_line = Block('yellow_line', 10, 50,
                    np.array([30, 255, 255]), np.array([20, 100, 100]))
# Detect 黄线
yellow_line_detect = Detect(yellow_cone, 'yellow_line_detect', 300, 20)

# Block 蓝色A4纸
blue_A4 = Block('blue_A4', 15, 15,
                np.array([124, 255, 255]), np.array([100, 43, 46]))
# Detect 蓝色A4纸
blue_A4_detect = Detect(blue_cone, 'blue_A4_detect', 180, 20)

# SIFT 左转
blue_left = Sift('blue_left')
blue_left.detect_and_compute(gray_Blue_Left)
# Matcher 左转
blue_left_matcher = Matcher('blue_left_matcher')

# SIFT 右转
blue_right = Sift('blue_right')
blue_right.detect_and_compute(gray_Blue_Right)
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
    return False


def A4_find(img):
    roi_resize = cv2.resize(img, (img.shape[0] // 2, img.shape[1] // 2))
    hsv_img = cv2.cvtColor(roi_resize, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_img, blue_A4.color_lower, blue_A4.color_upper)
    kernel = np.ones((40, 40), np.uint8)
    dilated_image = cv2.dilate(mask, kernel, iterations=1)
    contours, _ = cv2.findContours(dilated_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return blue_A4_detect.find_block(contours, return_mode=2)


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


def cone_detect(img, Cone, Cone_Detect):
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_img, Cone.color_lower, Cone.color_upper)
    kernel = np.ones((25, 25), np.uint8)
    dilated_image = cv2.dilate(mask, kernel, iterations=1)
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
    return False