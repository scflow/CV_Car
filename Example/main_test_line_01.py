import cv2
import time
import numpy as np
import flann
from loguru import logger
import yaml
import sys
import line
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
    logger.remove()
    setlog()
    start_time = time.time()
    cap = cv2.VideoCapture('../Material/pgv10.mp4')
    if not cap.isOpened():
        logger.error('Video Open Failed')
        exit()
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        img = line.show_lane(frame)
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
