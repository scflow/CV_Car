import cv2
import numpy as np
import math


def fitler_process(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    equalized = cv2.equalizeHist(gray)
    gaussian = cv2.GaussianBlur(equalized, (5, 5), 3)
    median = cv2.medianBlur(gaussian, 5)
    adaptive_thresh = cv2.adaptiveThreshold(median, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                            cv2.THRESH_BINARY, 9, 0)
    kernel = np.ones((3, 3), np.uint8)
    dilated_image = cv2.erode(adaptive_thresh, kernel, iterations=1)
    return dilated_image


def contour_extraction(img):
    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # 筛选轮廓
    lane_lines = []
    min_line_length = 300  # 跑道线最小长度，根据实际情况调整
    contour_areas = []  # 存储轮廓及其面积
    slope_threshold = 0.2
    for contour in contours:
        # 计算轮廓长度
        perimeter = cv2.arcLength(contour, True)
        if perimeter > min_line_length:
            # 计算轮廓的斜率
            x, y, w, h = cv2.boundingRect(contour)
            # if w == 0 or h == 0:
            if h == 0:
                continue  # 忽略太小或太大的轮廓
            if w == 0:
                if x < img.shape[1] / 2:
                    slope = 99
                else:
                    slope = -99
            else:
                slope = (y - (y + h)) / (x - (x + w))

            # 检查轮廓的斜率，以区分跑道线和噪点
            if abs(slope) > slope_threshold:
                lane_lines.append(contour)

    # # 初步筛选满足长度和斜率条件的轮廓
    # filtered_contours = []
    # for contour in contours:
    #     perimeter = cv2.arcLength(contour, True)
    #     if perimeter > min_line_length:
    #         x, y, w, h = cv2.boundingRect(contour)
    #         if w == 0 or h == 0:
    #             continue  # 忽略太小或太大的轮廓
    #         slope = (y - (y + h)) / (x - (x + w))  # 计算斜率
    #         if abs(slope) > slope_threshold:
    #             filtered_contours.append(contour)
    #
    # # 计算面积并保留最大的两个轮廓
    # if len(filtered_contours) > 0:
    #     contour_areas = [(contour, cv2.contourArea(contour)) for contour in filtered_contours]
    #     contour_areas.sort(key=lambda x: x[1], reverse=True)  # 按面积降序排序
    #     top_contours = contour_areas[:2]  # 保留面积最大的两个轮廓
    #     lane_lines = [contour for contour, area in top_contours]
    # else:
    #     lane_lines = []

    # 在空白图像上绘制轮廓
    line_image = np.zeros_like(img)
    for line in lane_lines:
        cv2.drawContours(line_image, [line], 0, (255, 255, 255), 3)

    kernel1 = np.ones((3, 3), np.uint8)

    # 应用膨胀操作
    dilated_image = cv2.dilate(line_image, kernel1, iterations=1)
    cv2.imshow('dilated_image', dilated_image)
    return dilated_image


def roi_mask(gray_img):
    h, w = gray_img.shape[:2]
    height = h
    width = w
    # 定义下半部分的四边形顶点坐标
    poly_pts = np.array([[[0, int(height * 1.00)], [0, int(height * 0.66)], [width, int(height * 0.66)], [width, int(height * 1.00)]]])

    # 创建一个与gray_img大小相同的零矩阵作为掩膜
    mask = np.zeros_like(gray_img)

    # 使用cv2.fillPoly填充掩膜下半部分
    mask = cv2.fillPoly(mask, pts=poly_pts, color=[255])

    # 应用掩膜
    img_mask = cv2.bitwise_and(gray_img, mask)
    cv2.imshow('img_mask', img_mask)
    return img_mask


def get_lines(edge_img):
    """
    获取edge_img中的所有线段
    :param edge_img: 标记边缘的灰度图
    """

    def calculate_slope(line, width):
        """
        计算线段line的斜率
        :param line: np.array([[x_1, y_1, x_2, y_2]])
        :param width:
        :return:
        """
        x_1, y_1, x_2, y_2 = line[0]
        if x_1 == x_2:
            if x_1 < width / 2:
                return 99
            else:
                return -99
        else:
            return (y_2 - y_1) / (x_2 - x_1)

    def reject_abnormal_lines(lines, threshold=0.1):
        """
        剔除斜率不一致的线段
        :param lines: 线段集合, [np.array([[x_1, y_1, x_2, y_2]]), np.array([[x_1, y_1, x_2, y_2]]),..., np.array([[x_1, y_1, x_2, y_2]])]
        @param threshold:
        """
        slopes = [calculate_slope(line, width) for line in lines]
        while len(lines) > 0:
            mean = np.mean(slopes)
            diff = [abs(s - mean) for s in slopes]
            idx = np.argmax(diff)
            if diff[idx] > threshold:
                slopes.pop(idx)
                lines.pop(idx)
            else:
                break
        return lines

    def least_squares_fit(lines):
        """
        将lines中的线段拟合成一条线段
        :param lines: 线段集合, [np.array([[x_1, y_1, x_2, y_2]]), np.array([[x_1, y_1, x_2, y_2]]), ...,
                                np.array([[x_1, y_1, x_2, y_2]])]
        :return: 线段上的两点, np.array([[x_min, y_min], [x_max, y_max]])
        """
        x_coords = np.ravel([x for line in lines for x in line[0][::2]])
        y_coords = np.ravel([y for line in lines for y in line[0][1::2]])
        poly = np.polyfit(x_coords, y_coords, deg=1)
        point_min = (np.min(x_coords), np.polyval(poly, np.min(x_coords)))
        point_max = (np.max(x_coords), np.polyval(poly, np.max(x_coords)))
        return np.array([point_min, point_max], dtype=np.int32)

    height, width = edge_img.shape[:2]
    # 获取所有线段
    lines = cv2.HoughLinesP(edge_img, 1, np.pi / 180, 15, minLineLength=50,
                            maxLineGap=50)
    # 按照斜率分成车道线
    if lines is not None:
        left_lines = [line for line in lines if calculate_slope(line, width) > 0]
    else:
        left_lines = []
    if lines is not None:
        right_lines = [line for line in lines if calculate_slope(line, width) < 0]
    else:
        right_lines = []
    # 剔除离群线段
    left_lines = reject_abnormal_lines(left_lines)
    right_lines = reject_abnormal_lines(right_lines)
    if not left_lines or not right_lines:
        return None, None  # 返回None表示没有检测到线段
    return least_squares_fit(left_lines), least_squares_fit(right_lines)


def show_lane(color_img, mode=0):
    fitler_img = fitler_process(color_img)
    contour_img = contour_extraction(fitler_img)
    mask_gray_img = roi_mask(contour_img)
    # contour_img = roi_mask(fitler_img)
    # mask_gray_img = contour_extraction(contour_img)

    if mask_gray_img is None:
        return color_img
    else:
        lines = get_lines(mask_gray_img)
        if lines[0] is None or lines[1] is None:
            return color_img
        else:
            right_line, left_line = lines
            if mode == 2:
                LeftLine.update(left_line)
                RightLine.update(right_line)
                if LeftLine.upper_x is not None and RightLine.upper_x is not None and LeftLine.upper_x < RightLine.upper_x:
                    MidLine.update(np.array([[(LeftLine.upper_x + RightLine.upper_x) / 2, MidLine.upper_y],
                                             [(LeftLine.lower_x + RightLine.lower_x) / 2, MidLine.lower_y]]))
                else:
                    MidLine.lose_count += 1
                    MidLine.lose_num += 1
                    if MidLine.lose_num == 5:
                        MidLine.upper_x = mask_gray_img.shape[1] // 2
                        MidLine.lose_num = 0
                if LeftLine.upper_x is not None:
                    cv2.line(color_img, [int(LeftLine.upper_x), MidLine.upper_y],
                             [int(LeftLine.lower_x), MidLine.lower_y],
                             color=(20, 50, 200), thickness=5)
                if RightLine.upper_x is not None:
                    cv2.line(color_img, [int(RightLine.upper_x), MidLine.upper_y],
                             [int(RightLine.lower_x), MidLine.lower_y],
                             color=(127, 127, 255), thickness=5)
                if MidLine.upper_x is not None:
                    cv2.line(color_img, [int(MidLine.upper_x), MidLine.upper_y],
                             [int(MidLine.lower_x), MidLine.lower_y],
                             color=(255, 127, 127), thickness=5)
            if mode == 2:
                color_img = draw_original_lines(color_img, lines)
            return color_img


def draw_original_lines(img, lines):
    """
    在img上绘制lines
    :param img:
    :param lines: 两条线段: [np.array([[x_min1, y_min1], [x_max1, y_max1]]),
                            np.array([[x_min2, y_min2], [x_max2, y_max2]])]
    :return:
    """
    left_line, right_line = lines
    cv2.line(img, tuple(left_line[0]), tuple(left_line[1]), color=(255, 255, 0),
             thickness=3)
    cv2.line(img, tuple(right_line[0]), tuple(right_line[1]),
             color=(0, 255, 255), thickness=3)
    return img


class Line:
    def __init__(self):
        self.upper_x = None
        self.upper_y = None
        self.lower_x = None
        self.lower_y = None
        self.slope = None
        self.cos = 1
        self.width = None
        self.height = None
        self.lose_count = 0
        self.lose_num = 0
        self.error_count = 0
        self.error_num = 0

    def set_y(self, upper_y, lower_y):
        self.upper_y = upper_y
        self.lower_y = lower_y

    def set_img(self, height, width):
        self.height = height
        self.width = width
        self.upper_y = int(self.height * 0.66)
        self.lower_y = int(self.height - 1)

    def update(self, line):
        [[x_1, y_1], [x_2, y_2]] = line
        if x_1 == x_2:
            self.slope = 99
            self.upper_x = x_1
            self.lower_x = x_1
        else:
            slope_tmp = (y_2 - y_1) / (x_2 - x_1)
            if slope_tmp == 0:
                slope_tmp = 0.01
            upper_x_tmp = x_1 - (y_1 - self.upper_y) / slope_tmp
            lower_x_tmp = x_1 - (y_1 - self.lower_y) / slope_tmp
            cos_tmp = math.sqrt(1 / (slope_tmp * slope_tmp + 1))
            if self.upper_x is not None:
                if abs(upper_x_tmp - self.upper_x) < 0.25 * self.width and abs(cos_tmp - self.cos) < 0.4:
                    self.upper_x = 0.75 * upper_x_tmp + 0.25 * self.upper_x
                    self.lower_x = 0.75 * lower_x_tmp + 0.25 * self.lower_x
                    self.slope = 0.75 * slope_tmp + 0.25 * self.slope
                    self.cos = 0.75 * cos_tmp + 0.25 * self.cos
                    self.error_num = 0
                else:
                    self.error_num += 1
                    self.error_count += 1
                    self.lose_count += 1
                    if self.error_num > 5:
                        self.upper_x = upper_x_tmp
                        self.lower_x = lower_x_tmp
                        self.slope = slope_tmp
                        self.cos = cos_tmp
            elif self.upper_x is None or self.lower_x is None and self.error_num > 5:
                self.lose_count += 1
                self.upper_x = upper_x_tmp
                self.lower_x = lower_x_tmp
                self.slope = slope_tmp
                self.cos = cos_tmp

    def get_points(self):
        return np.array([[self.upper_x, self.upper_y], [self.lower_x, self.lower_y]], dtype=np.int32)


LeftLine = Line()
RightLine = Line()
MidLine = Line()
