import cv2
import numpy as np


class Sift:
    """
    使用SIFT检测图像特征点，效果较好，但是计算量更大，推荐使用
    """
    def __init__(self, name):
        self.name = name
        self.sift = cv2.SIFT_create()
        self.kp = None
        self.des = np.array([])

    def detect_and_compute(self, gray_img):
        self.kp, self.des = self.sift.detectAndCompute(gray_img, None)


class ORB:
    """
    使用ORB检测图像特征点，计算量小，但是效果不如SIFT，不推荐使用
    """
    def __init__(self, name):
        self.name = name
        self.orb = cv2.ORB_create()
        self.kp = None
        self.des = np.array([])

    def detect_and_compute(self, gray_img):
        self.kp, self.des = self.orb.detectAndCompute(gray_img, None)


class Matcher:
    """
    特征匹配器，用于将两张图片进行特征点匹配
    """
    def __init__(self, name, algorithm=1, trees=5, checks=50):
        self.name = name
        self.algorithm = algorithm
        self.trees = trees
        self.checks = checks
        self.index_params = dict(algorithm=self.algorithm, trees=self.trees)
        self.search_params = dict(checks=self.checks)
        self.good = []
        self.goodnum = 0
        self.matches = None
        self.flann = cv2.FlannBasedMatcher(self.index_params, self.search_params)

    def knn_match(self, des1, des2, num=8, mode=0):
        """
        knn特诊匹配器,匹配两图像特征点
        :param des1:    源图片
        :param des2:    待检测图片
        :param num:     特诊点数量，默认为8
        :param mode:    模式选择 默认为0， 0返回特征点数量， 1返回bool值，匹配成功为真，否则为假
        :return:        根据mode选择返回值：0返回特征点数量， 1返回bool值，匹配成功为真，否则为假
        """
        self.clear_good()
        self.matches = self.flann.knnMatch(des1, des2, k=2)
        for i, (m, n) in enumerate(self.matches):
            if m.distance < 0.7 * n.distance:
                self.good.append(m)
        self.goodnum = len(self.good)
        if mode == 0:
            return self.goodnum
        if mode == 1:
            if self.goodnum >= num:
                return True
            else:
                return False

    def clear_good(self):
        """
        状态清除，清除已检测的特征点记录
        :return:        无返回值
        """
        self.good = []
        self.goodnum = 0


Blue_Left = cv2.imread('Picture/Blue_Left.jpg')
gray_Blue_Left = cv2.cvtColor(Blue_Left, cv2.COLOR_BGR2GRAY)
Blue_Right = cv2.imread('Picture/Blue_Right.jpg')
gray_Blue_Right = cv2.cvtColor(Blue_Right, cv2.COLOR_BGR2GRAY)

Red_Left = cv2.imread('Picture/Red_Left.jpg')
gray_Red_Left = cv2.cvtColor(Red_Left, cv2.COLOR_BGR2GRAY)
Red_Right = cv2.imread('Picture/Red_Right.jpg')
gray_Red_Right = cv2.cvtColor(Red_Right, cv2.COLOR_BGR2GRAY)

Blue_A = cv2.imread('Picture/Blue_A.jpg')
gray_Blue_A = cv2.cvtColor(Blue_A, cv2.COLOR_BGR2GRAY)
Blue_B = cv2.imread('Picture/Blue_B.jpg')
gray_Blue_B = cv2.cvtColor(Blue_B, cv2.COLOR_BGR2GRAY)

Red_A = cv2.imread('Picture/Red_A.jpg')
gray_Red_A = cv2.cvtColor(Red_A, cv2.COLOR_BGR2GRAY)
Red_B = cv2.imread('Picture/Red_B.jpg')
gray_Red_B = cv2.cvtColor(Red_B, cv2.COLOR_BGR2GRAY)

Turn_Left = cv2.imread('Picture/Turn_Left.jpg')
gray_Turn_Left = cv2.cvtColor(Turn_Left, cv2.COLOR_BGR2GRAY)
Turn_Right = cv2.imread('Picture/Turn_Right.jpg')
gray_Turn_Right = cv2.cvtColor(Turn_Right, cv2.COLOR_BGR2GRAY)
