import cv2
import time
import numpy as np
import onnxruntime


class FastestDet:
    def __init__(self, model_path='FastestDet.onnx', input_width=512, input_height=512, thresh=0.70):
        self.input_width = input_width
        self.input_height = input_height
        self.thresh = thresh
        self.session = onnxruntime.InferenceSession(model_path)

    @staticmethod
    def sigmoid(x):
        return 1. / (1 + np.exp(-x))

    @staticmethod
    def tanh(x):
        return 2. / (1 + np.exp(-2 * x)) - 1

    @staticmethod
    def preprocess(src_img, size):
        output = cv2.resize(src_img, (size[0], size[1]), interpolation=cv2.INTER_AREA)
        output = output.transpose(2, 0, 1)
        output = output.reshape((1, 3, size[1], size[0])).astype('float32') / 255.0
        return output

    @staticmethod
    def nms(dets, thresh=0.5):
        x1 = dets[:, 0]
        y1 = dets[:, 1]
        x2 = dets[:, 2]
        y2 = dets[:, 3]
        scores = dets[:, 4]
        areas = (x2 - x1 + 1) * (y2 - y1 + 1)
        order = scores.argsort()[::-1]
        keep = []

        while order.size > 0:
            i = order[0]
            keep.append(i)

            xx1 = np.maximum(x1[i], x1[order[1:]])
            yy1 = np.maximum(y1[i], y1[order[1:]])
            xx2 = np.minimum(x2[i], x2[order[1:]])
            yy2 = np.minimum(y2[i], y2[order[1:]])

            w = np.maximum(0.0, xx2 - xx1 + 1)
            h = np.maximum(0.0, yy2 - yy1 + 1)
            inter = w * h

            ovr = inter / (areas[i] + areas[order[1:]] - inter)

            inds = np.where(ovr <= thresh)[0]
            order = order[inds + 1]

        output = []
        for i in keep:
            output.append(dets[i].tolist())

        return output

    def detection(self, img, target_cls_indices):
        H, W, _ = img.shape
        data = self.preprocess(img, [self.input_width, self.input_height])
        input_name = self.session.get_inputs()[0].name
        # 只获取模型的输出
        feature_map = self.session.run(None, {input_name: data})[0][0].transpose(1, 2, 0)
        feature_map_height, feature_map_width = feature_map.shape[:2]

        # 取出目标分数和类别分数
        obj_scores = feature_map[..., 0]  # 取出目标分数
        cls_scores = feature_map[..., 5:5 + len(target_cls_indices)]  # 取出类别分数
        # 计算分数
        scores = (obj_scores[..., np.newaxis] ** 0.6) * (cls_scores ** 0.4)

        # 检测目标类别是否存在
        cls_found = {idx: False for idx in target_cls_indices}

        for idx, cls_index in enumerate(target_cls_indices):
            if np.any(scores[..., idx] > self.thresh):  # 检查是否存在该类别
                cls_found[cls_index] = True

        return cls_found


if __name__ == '__main__':
    img = cv2.imread(r"0008.jpg")
    detector = FastestDet()

    target_cls_indices = [0, 1]  # 要检测的类别索引
    start = time.perf_counter()
    cls_found = detector.detection(img, target_cls_indices)
    end = time.perf_counter()
    elapsed_time = (end - start) * 1000.
    print("forward time:%fms" % elapsed_time)

    if cls_found[0] and not cls_found[1]:
        print("只存在类别 0")
    elif cls_found[1] and not cls_found[0]:
        print("只存在类别 1")
    elif cls_found[0] and cls_found[1]:
        print("同时存在类别 0 和 1")
    else:
        print("两类都不存在")
