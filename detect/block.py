import cv2
import numpy as np


class Block:
    """
    单一颜色物块
    """
    def __init__(self, name, min_h, min_w, color_upper=np.array([]), color_lower=np.array([])):
        self.name = name
        self.min_h = min_h
        self.min_w = min_w
        self.color_upper = color_upper
        self.color_lower = color_lower

    def set_minsize(self, min_h, min_w):
        self.min_h = min_h
        self.min_w = min_w

    def set_color(self, color_upper, color_lower):
        self.color_upper = color_upper
        self.color_lower = color_lower


class Detect(Block):
    """
    单一颜色物块检测,继承物块对象以获取其部分信息
    """
    def __init__(self, parent_object, name, line_high, offset):
        super().__init__(parent_object.name, parent_object.min_h, parent_object.min_w)
        self.name = name
        self.offset = offset
        self.line_high = line_high
        self.num = 0
        self.sum = 0
        self.effective = []
        self.min_h = parent_object.min_h
        self.min_w = parent_object.min_w

    def clear_effective(self):
        """
        状态清除函数，清除self.effective保存的记录
        :return:
        """
        self.effective = []
        self.num = 0

    def find_block(self, contours, print_mode=0, return_mode=0):
        """
        物块检测函数，通过判断轮廓中心是否通过检测线判断是否有物块，轮廓需通过hsv和mask筛选出目标颜色后的图片按需求处理后得到的轮廓，
        不同目标的检测方法和特征差异较大，不提供函数统一处理，需自行处理
        :param contours:        轮廓
        :param print_mode:      print模式判断，默认为0，若检测到物块则会打印物块坐标,若为1，则不打印输出
        :param return_mode:     返回值模式选择，默认为0，返回检测总数量，若为1，返回总数量和本次检测出的数量
                                若为2，返回bool值，检测到返回真，否则假
        :return:                默认mode为0，返回检测总数量，若为1，返回总数量和本次检测出的数量
                                若为2，返回bool值，检测到返回真，否则假
        """
        self.clear_effective()
        for (index, contour) in enumerate(contours):
            (x, y, w, h) = cv2.boundingRect(contour)
            isValid = (w >= self.min_w) and (h >= self.min_h)
            if not isValid:
                continue
            point = center(x, y, w, h)
            self.effective.append(point)
            for (_, center_y) in self.effective:
                if (center_y > self.line_high - self.offset) and (center_y < self.line_high + self.offset):
                    self.num += 1
                    self.sum += 1
                    self.effective.remove((_, center_y))
                    if print_mode == 0:
                        print(f'{self.name} Result x: {x}, y: {y}, w: {w}, h: {h}')

        return_map = {
            0: self.sum,
            1: (self.num, self.sum),
            2: self.num > 0
        }
        return return_map.get(return_mode)


def center(block_x, block_y, block_w, block_h):
    return int(block_x + block_w / 2), int(block_y + block_h / 2)
