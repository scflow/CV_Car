# 视频录制保存使用示例

```python
import cv2

if __name__ == '__main__':
    capture = cv2.VideoCapture('videopath')
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    output = cv2.VideoWriter("output.mp4", cv2.VideoWriter_fourcc(*"mp4v"), 60, (width, height))
    while True:
        ret, frame = capture.read()
        output.write(frame)
    capture.release()
    output.release()
```

