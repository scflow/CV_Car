import cv2
import multiprocessing as mp
import numpy as np
import time
import object
import line
from loguru import logger
import sys
import yaml
from utils import FPS
from multiprocessing.sharedctypes import Value, Array
from ctypes import *


def setlog():
    with open(r'log\loguru_config.yaml', 'r', encoding="utf-8") as file:
        # config = yaml.safe_load(file)
        config = yaml.safe_load(file)
    for handler_name, handler_config in config['handlers'].items():
        if handler_name == 'console':
            logger.add(sink=sys.stdout, level=handler_config['level'])
        elif handler_name == 'file':
            logger.add(sink=handler_config['sink'], level=handler_config['level'],
                       rotation=handler_config['rotation'], retention=handler_config['retention'])


def process_line(img):
    line_img = line.show_lane(img)


def process_find(img):
    global Cone_Judge
    global Cone_Angle

    if Cone_Detect.get_sum() < 3:
        if Cone_Judge == 0:
            Cone_Angle = 0
            Cone_Detect.set_num(0)
            image_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(image_hsv, Yellow_Cone.color_lower, Yellow_Cone.color_upper)
            kernel = np.ones((25, 25), np.uint8)
            dilated_image = cv2.dilate(mask, kernel, iterations=1)
            contours, _ = cv2.findContours(dilated_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            Cone_Detect.find_object(contours, img)
            effective = Cone_Detect.effective
            Cone_Detect.clear_effective()
            for (mx, my, x, y, w, h) in Cone_Detect.effective:
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.line(img, (10, Cone_Detect.get_line_high()), (1200, Cone_Detect.get_line_high()), (255, 255, 0), 3)
            cv2.putText(img, "    Cones Num:" + str(Cone_Detect.get_num()) + "    Cones Sum" + str(Cone_Detect.get_sum()),
                        (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 240, 10), 2)
            if Cone_Detect.get_num() > 0:
                Cone_Judge = 30
                if Cone_Detect.get_sum() % 2 == 0:
                    Cone_Angle = 5
                else:
                    Cone_Angle = -5
        else:
            Cone_Judge -= 1


def main():
    fps = FPS().start()
    logger.info(f'{time.asctime()}, demo start running')
    cap = cv2.VideoCapture("../Material/pgv7.mp4")  # 使用摄像头作为视频输入
    # cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("无法打开摄像头")
        return
    pool = mp.Pool(processes=2)
    start_time = time.time()
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        current_time = time.time() - start_time
        # tasks = []
        # tasks.append(pool.apply_async(process_line, args=(frame,)))
        # tasks.append(pool.apply_async(process_find, args=(frame,)))
        pool.apply_async(process_line, args=(frame,))
        pool.apply_async(process_find, args=(frame,))
        # 收集并处理结果
        # results = [task.get() for task in tasks]
        # find_img = results[1]
        # res1 = q1.get()
        # res2 = q2.get()
        # cv2.imshow('results[0]', res1)
        # cv2.imshow('results[1]', res2)
        # cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        fps.update()
        fps.stop()
    logger.info("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
    logger.info("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

    cap.release()
    cv2.destroyAllWindows()
    pool.close()
    pool.join()
    exit()


Yellow_Cone = object.Object('Yellow_Cone', 4, 4)
Cone_Detect = object.Detect(Yellow_Cone, 'Cone_Detect', 430, 10)
Yellow_Cone.set_color(np.array([20, 100, 100]), np.array([30, 255, 255]))

Cone_Judge = 0
Cone_Angle = 0
Car_Angle = 90
Line_Angle = 0


if __name__ == '__main__':
    logger.remove(None)
    setlog()
    main()
