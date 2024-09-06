import cv2
import time
import numpy as np
import multiprocessing
import threading
import flann
import line
import object
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from log import log


if __name__ == "__main__":
    start_time = time.time()
    log.set_logging()
    logger = log.logging.getLogger("application")
    cap = cv2.VideoCapture('../Material/pgv7.mp4')
    Yellow_Cone = object.Object('Yellow_Cone', 15, 15)
    logger.info(f'{Yellow_Cone.get_minsize()}')
    Cone_Detect = object.Detect(Yellow_Cone, 'Cone_Detect', 416, 3)
    Yellow_Cone.set_color(np.array([20, 100, 100]), np.array([30, 255, 255]))
    if not cap.isOpened():
        logger.error("Camera 0 Open Failed")
        exit()
    while True:
        loop_start_time = time.time()
        ret, frame = cap.read()
        image_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(image_hsv, Yellow_Cone.color_lower, Yellow_Cone.color_upper)
        kernel = np.ones((25, 25), np.uint8)
        dilated_image = cv2.dilate(mask, kernel, iterations=1)
        cv2.imshow('mask', dilated_image)
        contours, _ = cv2.findContours(dilated_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        Cone_Detect.find_object(contours, frame)
        for (mx, my, x, y, w, h) in Cone_Detect.effective:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv2.line(frame, (10, Cone_Detect.get_line_high()), (1200, Cone_Detect.get_line_high()), (255, 255, 0), 3)
        cv2.putText(frame, "    Cones Num:" + str(Cone_Detect.get_num()) + "    Cones Sum" + str(Cone_Detect.get_sum()), (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 240, 10), 2)
        Cone_Detect.set_num(0)
        cv2.imshow('video', frame)
        Cone_Detect.clear_effective()
        current_time = time.time()
        loop_current_time = time.time()
        cost_time = current_time - start_time
        loop_cost_time = loop_current_time - loop_start_time
        if not ret:
            logger.error("Unable to receive frame, please exit")
            break
        if cv2.waitKey(20) & 0xFF == ord('q'):
            break
