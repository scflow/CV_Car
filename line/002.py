import cv2
import numpy as np
import math


def fitler_process(color_img):
    gray = cv2.cvtColor(color_img, cv2.COLOR_BGR2GRAY)
    equalized = cv2.equalizeHist(gray)
    wb = cv2.cvtColor(equalized, cv2.COLOR_GRAY2BGR)
    wbi = cv2.cvtColor(wb, cv2.COLOR_BGR2GRAY)
    gaussian = cv2.GaussianBlur(wbi, (5, 5), 3)
    # 高斯滤波去除噪点
    zhongzhi = cv2.medianBlur(gaussian, 5)
    # 中值滤波去除噪点
    adaptive_thresh = cv2.adaptiveThreshold(zhongzhi, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                            cv2.THRESH_BINARY, 9, 0)
    # image = cv2.Canny(adaptive_thresh,150,200)
    # sobel_x = cv2.Sobel(adaptive_thresh, cv2.CV_64F, 1, 0, ksize=3)
    '''
    hsv = cv2.cvtColor(color_img, cv2.COLOR_BGR2HSV)
    equalized_img = cv2.equalizeHist(hsv)
    lower_white = np.array([120, 60, 100])
    upper_white = np.array([200, 80, 255])
    mask = cv2.inRange(hsv, lower_white, upper_white)

    #img1 = cv2.GaussianBlur(mask,(5,5),5)

    kernel = np.ones((1,1),np.uint8)
    img2 = cv2.erode(mask,kernel,iterations=3)

    #img3 = cv2.medianBlur(img2,3)
    sobel_x = cv2.Sobel(img2, cv2.CV_64F, 1, 0, ksize=1)
    

    return equalized_img
    '''
    kernel1 = np.ones((3, 3), np.uint8)

    # 应用删减操作
    dilated_image = cv2.erode(adaptive_thresh, kernel1, iterations=1)

    return dilated_image


def contour(img):
    """
    def calculate_curve(contour):
        # 使用近似轮廓来计算曲率
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        # 计算曲率
        # 这里简化为计算轮廓点到其拟合直线距离的平均值
        # 实际应用中可能需要更复杂的计算方法
        if len(approx) > 2:
            [vx, vy, x, y] = cv2.fitLine(approx, cv2.DIST_L2, 0, 0.01, 0.01)
            distances = []
            for point in approx:
                x1, y1 = point[0]
                distance = np.abs(vy * x1 - vx * y1 + x * vy - y * vx) / np.sqrt(vx ** 2 + vy ** 2)
                distances.append(distance)
            curve = np.mean(distances)
            return curve
        else:
            return 0  # 如果轮廓点太少，无法计算曲率，返回0
    """
    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 筛选轮廓
    lane_lines = []
    min_line_length = 300  # 跑道线最小长度，根据实际情况调整
    '''
    image_center_x = img.shape[1] / 2  # 图像中心的x坐标
    for contour in contours:
        perimeter = cv2.arcLength(contour, True)
        if perimeter > min_line_length:
            x, y, w, h = cv2.boundingRect(contour)
            if w == 0 or h == 0:
                continue
            slope = (y - (y + h)) / (x - (x + w))
            if abs(slope) > 0.2:
                M = cv2.moments(contour)
                cX = int(M["m10"] / M["m00"]) if M["m00"] != 0 else 0
                # 计算轮廓到中心的距离
                distance_to_center = abs(cX - image_center_x)
                # 添加轮廓到列表，不添加距离
                lane_lines.append(contour)

    # 分离左右两边的轮廓
    left_lane_lines = [line for line in lane_lines if line[0][0][0] < image_center_x]
    right_lane_lines = [line for line in lane_lines if line[0][0][0] > image_center_x]

    # 如果轮廓的数量大于2，选择离图像中心最近的左轮廓和最远的右轮廓
    if len(left_lane_lines) > 2:
        left_lane_lines.sort(key=lambda x: x[0][0][0])
        selected_left_line = left_lane_lines[0]
    else:
        selected_left_line = left_lane_lines

    if len(right_lane_lines) > 2:
        right_lane_lines.sort(key=lambda x: x[0][0][0], reverse=True)
        selected_right_line = right_lane_lines[0]
    else:
        selected_right_line = right_lane_lines
    lane_lines = selected_right_line + selected_left_line


    '''
    for contour in contours:
        # 计算轮廓长度
        perimeter = cv2.arcLength(contour, True)
        if perimeter > min_line_length:
            # 计算轮廓的斜率
            x, y, w, h = cv2.boundingRect(contour)
            if w == 0 or h == 0:
                continue  # 忽略太小或太大的轮廓
            slope = (y - (y + h)) / (x - (x + w))

            # 检查轮廓的斜率，以区分跑道线和噪点
            if abs(slope) > 0.2:
                lane_lines.append(contour)
                # 计算轮廓的曲率
                #curve = calculate_curve(contour)

                # 根据曲率筛选轮廓
                #if curve > 0.1:  # some_threshold 是您设定的曲率阈值
                #lane_lines.append(contour)

    # 在空白图像上绘制轮廓
    line_image = np.zeros_like(img)
    for line in lane_lines:
        cv2.drawContours(line_image, [line], 0, (255, 255, 255), 3)

    kernel1 = np.ones((3, 3), np.uint8)

    # 应用膨胀操作
    dilated_image = cv2.dilate(line_image, kernel1, iterations=1)
    edges_img = cv2.Canny(dilated_image, 120, 200)
    # edges_img = cv2.Sobel(dilated_image, cv2.CV_64F, 1, 0, ksize=1)

    return dilated_image


def roi_mask(gray_img):
    h, w = gray_img.shape[:2]
    height = h
    width = w
    # 定义下半部分的四边形顶点坐标
    poly_pts = np.array([[[0, height], [0, int(height * 0.66)], [width, int(height * 0.66)], [width, height]]])

    # 创建一个与gray_img大小相同的零矩阵作为掩膜
    mask = np.zeros_like(gray_img)

    # 使用cv2.fillPoly填充掩膜下半部分
    mask = cv2.fillPoly(mask, pts=poly_pts, color=[255])

    # 应用掩膜
    img_mask = cv2.bitwise_and(gray_img, mask)

    return img_mask


def get_lines(edge_img):
    """
    获取edge_img中的所有线段
    :param edge_img: 标记边缘的灰度图
    """

    def calculate_slope(line):
        """
        计算线段line的斜率
        :param line: np.array([[x_1, y_1, x_2, y_2]])
        :return:
        """
        global new_width
        global new_height
        x_1, y_1, x_2, y_2 = line[0]
        if x_1 == x_2:
            if x_1 < new_width / 2:
                return 99
            else:
                return -99
        else:
            return (y_2 - y_1) / (x_2 - x_1)

    def reject_abnormal_lines(lines, threshold=0.1):
        """
        剔除斜率不一致的线段
        :param lines: 线段集合, [np.array([[x_1, y_1, x_2, y_2]]), np.array([[x_1, y_1, x_2, y_2]]),..., np.array([[x_1, y_1, x_2, y_2]])]
        """
        slopes = [calculate_slope(line) for line in lines]

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
        :param lines: 线段集合, [np.array([[x_1, y_1, x_2, y_2]]),np.array([[x_1, y_1, x_2, y_2]]),...,np.array([[x_1, y_1, x_2, y_2]])]
        :return: 线段上的两点, np.array([[xmin, ymin], [xmax, ymax]])
        """

        # x_coords = np.ravel([[line[0][0], line[0][2]] for line in lines])
        # y_coords = np.ravel([[line[0][1], line[0][3]] for line in lines])
        x_coords = np.ravel([x for line in lines for x in line[0][::2]])
        y_coords = np.ravel([y for line in lines for y in line[0][1::2]])
        poly = np.polyfit(x_coords, y_coords, deg=1)
        point_min = (np.min(x_coords), np.polyval(poly, np.min(x_coords)))
        point_max = (np.max(x_coords), np.polyval(poly, np.max(x_coords)))
        return np.array([point_min, point_max], dtype=np.int32)

    # 获取所有线段
    lines = cv2.HoughLinesP(edge_img, 1, np.pi / 180, 15, minLineLength=50,
                            maxLineGap=50)
    # 按照斜率分成车道线
    if lines is not None:
        left_lines = [line for line in lines if calculate_slope(line) > 0]
    else:
        left_lines = []
    if lines is not None:
        right_lines = [line for line in lines if calculate_slope(line) < 0]
    else:
        right_lines = []
    # 剔除离群线段
    left_lines = reject_abnormal_lines(left_lines)
    right_lines = reject_abnormal_lines(right_lines)
    if not left_lines or not right_lines:
        return None, None  # 返回None表示没有检测到线段
    return least_squares_fit(left_lines), least_squares_fit(right_lines)


def draw_lines(img, lines):
    """
    在img上绘制lines
    :param img:
    :param lines: 两条线段: [np.array([[xmin1, ymin1], [xmax1, ymax1]]), np.array([[xmin2, ymin2], [xmax2, ymax2]])]
    :return:
    """
    left_line, right_line = lines
    cv2.line(img, tuple(left_line[0]), tuple(left_line[1]), color=(255, 255, 0),
             thickness=5)
    cv2.line(img, tuple(right_line[0]), tuple(right_line[1]),
             color=(0, 255, 255), thickness=5)


def show_lane(color_img):
    global count
    ig0 = fitler_process(color_img)
    ig1 = contour(ig0)
    mask_gray_img = roi_mask(ig1)

    if mask_gray_img is None:
        cv2.imshow('mask', mask_gray_img)
        return color_img
    else:
        lines = get_lines(mask_gray_img)
        if lines[0] is None or lines[1] is None:
            cv2.line(color_img, [int(LeftLine.upper_point), MidLine.upper_y],
                     [int(LeftLine.lower_point), MidLine.lower_y],
                     color=(20, 50, 200), thickness=3)
            cv2.line(color_img, [int(RightLine.upper_point), MidLine.upper_y],
                     [int(RightLine.lower_point), MidLine.lower_y],
                     color=(127, 127, 255), thickness=3)
            cv2.line(color_img, [int(MidLine.upper_point), MidLine.upper_y],
                     [int(MidLine.lower_point), MidLine.lower_y],
                     color=(255, 127, 127), thickness=3)
            return color_img
        else:
            right_line, left_line = lines
            if count >= 20:
                LeftLine.set_points(left_line)
                RightLine.set_points(right_line)
                # LeftLine.upper_point = limit(LeftLine.upper_point, -0.1 * new_width, 0.5 * new_height)
                # LeftLine.lower_point = limit(LeftLine.lower_point, -3 * new_width, 0.5 * new_height)
                # RightLine.upper_point = limit(RightLine.upper_point, 0.5 * new_width, 1.1 * new_height)
                # RightLine.lower_point = limit(RightLine.lower_point, 0.5 * new_width, 4 * new_height)
                MidLine.set_points(
                    np.array([[(LeftLine.upper_point + RightLine.upper_point) / 2, MidLine.upper_y],
                              [(LeftLine.lower_point + RightLine.lower_point) / 2, MidLine.lower_y]]))
                cv2.line(color_img, [int(LeftLine.upper_point), MidLine.upper_y],
                         [int(LeftLine.lower_point), MidLine.lower_y],
                         color=(20, 50, 200), thickness=3)
                cv2.line(color_img, [int(RightLine.upper_point), MidLine.upper_y],
                         [int(RightLine.lower_point), MidLine.lower_y],
                         color=(127, 127, 255), thickness=3)
                cv2.line(color_img, [int(MidLine.upper_point), MidLine.upper_y],
                         [int(MidLine.lower_point), MidLine.lower_y],
                         color=(255, 127, 127), thickness=3)
            # draw_lines(color_img, lines)
            return color_img


def limit(num, limit_min, limit_max):
    if num < limit_min:
        return limit_min
    elif num > limit_max:
        return limit_max
    else:
        return num


class Line:
    global count

    def __init__(self):
        self.upper_point = None
        self.lower_point = None
        self.slope = None
        self.upper_y = None
        self.lower_y = None
        self.cos = 1

    def set_y(self, upper_y, lower_y):
        self.upper_y = upper_y
        self.lower_y = lower_y

    def set_points(self, line):
        [[x_1, y_1], [x_2, y_2]] = line
        if x_1 == x_2:
            self.slope = 999
            self.upper_point = x_1
            self.lower_point = x_1
        else:
            slope_tmp = (y_2 - y_1) / (x_2 - x_1)
            if slope_tmp == 0:
                slope_tmp = 0.01
            upper_point_tmp = x_1 - (y_1 - self.upper_y) / slope_tmp
            lower_point_tmp = x_1 - (y_1 - self.lower_y) / slope_tmp
            cos_tmp = math.sqrt(1 / (slope_tmp * slope_tmp + 1))
            if self.upper_point is not None:
                if count >= 50:
                    if abs(upper_point_tmp - self.upper_point) < 0.4 * new_width and abs(cos_tmp - self.cos) < 0.7:
                        self.upper_point = 0.75 * upper_point_tmp + 0.25 * self.upper_point
                        self.lower_point = 0.75 * lower_point_tmp + 0.25 * self.lower_point
                        self.slope = 0.75 * slope_tmp + 0.25 * self.slope
                        self.cos = 0.75 * cos_tmp + 0.25 * self.cos
            elif self.upper_point is None:
                self.upper_point = upper_point_tmp
                self.lower_point = lower_point_tmp
                self.slope = slope_tmp
                self.cos = cos_tmp

    def get_points(self):
        return np.array([[self.upper_point, self.upper_y], [self.lower_point, self.lower_y]], dtype=np.int32)


LeftLine = Line()
RightLine = Line()
MidLine = Line()
if __name__ == '__main__':
    count = 0
    capture = cv2.VideoCapture(r'E:\one\Movie\突击联队\VID_20231121_130118.mp4')
    # capture = cv2.VideoCapture('../Material/极限竞速：地平线 4 2024-07-20 16-53-31.mp4')
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = capture.get(cv2.CAP_PROP_FPS)
    new_width = width // 2
    new_height = height // 2
    output = cv2.VideoWriter("output.mp4", cv2.VideoWriter_fourcc(*"mp4v"), 60, (new_width, new_height))
    # last_frame = None  # 用于保存最后一帧
    LeftLine.set_y(int(0.66 * new_height), new_height - 1)
    RightLine.set_y(int(0.66 * new_height), new_height - 1)
    MidLine.set_y(int(0.66 * new_height), new_height - 1)
    angle = int(0.5 * new_width)
    angle_last = int(0.5 * new_width)
    cha = 0
    cha_last = 0
    while True:
        ret, frame = capture.read()
        if not ret:
            print("视频播放完成")
            break
            # if last_frame is not None:  # 确保我们有一个有效的帧
            #     resized_frame = cv2.resize(last_frame, (new_width, new_height))
            #     cv2.imshow('frame', resized_frame)
            #     key = cv2.waitKey(0)  # 等待按键事件
            #     if key == ord('q') or key == 27 or cv2.getWindowProperty('frame', cv2.WND_PROP_VISIBLE) < 1:
            #         break
            # else:
            #     break  # 如果没有有效的帧，退出循环
        else:
            last_frame = frame.copy()  # 保存当前帧作为最后一帧
            resized_frame = cv2.resize(last_frame, (new_width, new_height))
            # resized_frame = draw_border(resized_frame)
            frame = show_lane(resized_frame)
            # cv2.line(frame, [int(0.2 * new_width), int(0.8 * new_height)], [int(0.8 * new_width), int(0.8 * new_height)],
            #          color=(255, 50, 100), thickness=5)
            cv2.rectangle(frame, (int(0.4 * new_width), int(0.13 * new_height) - 20),
                          (int(0.6 * new_width), int(0.13 * new_height) + 20),
                          (0, 0, 0), -1)
            cv2.circle(frame, (int(0.4 * new_width), int(0.13 * new_height)), 20, (0, 0, 0), -1)
            cv2.circle(frame, (int(0.6 * new_width), int(0.13 * new_height)), 20, (0, 0, 0), -1)
            if count < 20:
                count += 1
            else:
                count += 1
                cha = 0.25 * (MidLine.upper_point - MidLine.lower_point)
                angle += int(cha - cha_last)
                angle = limit(angle, 0.4 * new_width, 0.6 * new_width)
                angle += 0.4 * (angle_last - angle)
            cv2.circle(frame, (int(angle), int(0.13 * new_height)), 15, (255, 255, 255), -1)
            cha_last = cha
            angle_last = angle
            output.write(frame)
            cv2.imshow('frame', frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27 or cv2.getWindowProperty('frame', cv2.WND_PROP_VISIBLE) < 1:
                break
    capture.release()
    output.release()
    cv2.destroyAllWindows()
    exit()
