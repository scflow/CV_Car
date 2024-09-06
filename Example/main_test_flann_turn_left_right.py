import cv2
import time
import numpy as np
import flann
from loguru import logger
import yaml
import sys
from utils import FPS
import object


def setlog():
    with open('log/loguru_config.yaml', 'r', encoding="utf-8") as file:
        config = yaml.safe_load(file)
    for handler_name, handler_config in config['handlers'].items():
        if handler_name == 'console':
            logger.add(sink=sys.stdout, level=handler_config['level'])
        elif handler_name == 'file':
            logger.add(sink=handler_config['sink'], level=handler_config['level'],
                       rotation=handler_config['rotation'], retention=handler_config['retention'])


if __name__ == "__main__":
    start_time = time.time()
    fps = FPS().start()
    logger.remove(None)
    setlog()
    # cap = cv2.VideoCapture(0)
    cap = cv2.VideoCapture('../Material/pgv13.mp4')
    Blue_A4 = object.Object('Blue_A4', 10, 10)
    A4_Detect = object.Detect(Blue_A4, 'A4_Detect', 90, 20)
    Blue_A4.set_color(np.array([100, 43, 46]), np.array([124, 255, 255]))
    blue_left = flann.Element('blue_left')
    blue_right = flann.Element('blue_right')
    blue_left_img = cv2.imread('Picture/Blue_Left.jpg')
    blue_left_gray = cv2.cvtColor(blue_left_img, cv2.COLOR_BGR2GRAY)
    blue_right_img = cv2.imread('Picture/Blue_Right.jpg')
    blue_right_gray = cv2.cvtColor(blue_right_img, cv2.COLOR_BGR2GRAY)
    blue_left.detect_and_compute(blue_left_gray)
    blue_right.detect_and_compute(blue_right_gray)
    turn_left = flann.Matcher('turn_left')          # 左转匹配器，用于视频画面与左转图片进行特征匹配
    turn_right = flann.Matcher('turn_right')        # 右转匹配器，用于视频画面与右转图片进行特征匹配
    frame_detect = flann.Element('frame_detect')    # 视频画面特征提取器，用于提取视频画面的中特征点
    A4 = 0
    if not cap.isOpened():
        logger.error("Camera 0 Open Failed")
        exit()
    while True:
        loop_start_time = time.time()
        ret, frame = cap.read()
        if not ret:
            logger.error("Unable to receive frame, please exit")
            break
        cv2.imshow('frame', frame)
        if A4 == 0:
            roi_frame = frame[150:400, 300:600]
            roi_resize = cv2.resize(roi_frame, (roi_frame.shape[0]//2, roi_frame.shape[1]//2))
            image_hsv = cv2.cvtColor(roi_resize, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(image_hsv, Blue_A4.color_lower, Blue_A4.color_upper)
            kernel = np.ones((40, 40), np.uint8)
            dilated_image = cv2.dilate(mask, kernel, iterations=1)
            cv2.imshow('mask', dilated_image)
            contours, _ = cv2.findContours(dilated_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            A4_Detect.find_object(contours, frame)
            if A4_Detect.get_sum() > 0:
                A4 += 1
        elif A4 == 1:
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            roi_frame = gray_frame[250:400, 300:600]
            cv2.imshow('roi_frame', roi_frame)
            frame_detect.detect_and_compute(roi_frame)
            turn_right.knn_match(blue_right.get_des(), frame_detect.get_des())
            turn_left.knn_match(blue_left.get_des(), frame_detect.get_des())
            if turn_right.get_goodnum() > 7:
                logger.info(f'turn right goodnum = {turn_right.get_goodnum()}')
                A4 = 2
            if turn_left.get_goodnum() > 7:
                logger.info(f'turn left, goodnum = {turn_left.get_goodnum()}')
                A4 = 2
            turn_left.clear_good()
            turn_right.clear_good()
        if cv2.waitKey(20) & 0xFF == ord('q'):
            break
        fps.update()
        fps.stop()
    logger.info("elapsed time: {:.2f}".format(fps.elapsed()))
    logger.info("approx. FPS: {:.2f}".format(fps.fps()))
    cap.release()
    cv2.destroyAllWindows()
    logger.info('Program Finish')
    exit()
