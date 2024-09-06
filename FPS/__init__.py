"""
功能 统计FPS

example

    from FPS.utils import FPS

    if __name__ == "__main__":
        fps = FPS().start()
        cap = cv2.VideoCapture(Path)
        while True:
            ret, frame = cap.read()
            ...
            fps.update()
        fps.stop()
        print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
        print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
        cap.release()

"""

__version__ = "0.1.0"

from . import utils
