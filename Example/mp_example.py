import cv2
import multiprocessing
import time
from NewCode import code


def process_line(input_queue, output_queue, src2=0, src3=0):
    """
    巡线进程函数
    :param input_queue:     输入队列，包括frame以及frame_count
    :param output_queue:    输出队列，将子数据编码后发出
    :param src2:            子数据2，初始值为0
    :param src3:            子数据3，初始值为0
    :return:                output_queue 输出队列
    """

    while True:
        # 超时判断，若队列接受超时，将退出while循环并在输出队列put None终结队列
        try:
            pdata = input_queue.get(timeout=2)
        except multiprocessing.queues.Empty:
            break
        if pdata is None:
            break
        (img, img_count) = pdata
        output_queue.put(code.encode(img_count, src2, src3))
    output_queue.put(None)


def process_find(input_queue, output_queue, src2=0, src3=0):
    """
    检测进程函数
    :param input_queue:     输入队列，包括frame以及frame_count
    :param output_queue:    输出队列，将子数据编码后发出
    :param src2:            子数据2，初始值为0
    :param src3:            子数据3，初始值为0
    :return:                output_queue 输出队列
    """

    while True:
        # 超时判断，若队列接受超时，将退出while循环并在输出队列put None终结队列
        try:
            pdata = input_queue.get(timeout=2)
        except multiprocessing.queues.Empty:
            break
        if pdata is None:
            break
        (img, img_count) = pdata
        output_queue.put(code.encode(img_count, src2, src3))
    output_queue.put(None)


def process_combine(input1_queue, input2_queue, output_queue):
    """
    数据整合进程，将巡线与检测进程传来的数据进行综合处理编码后在输出队列put
    :param input1_queue:    输入队列1，接收队列1的数据
    :param input2_queue:    输入队列2，接收队列1的数据
    :param output_queue:    输出队列，将子数据编码后发出
    :return:                output_queue 输出队列
    """

    while True:
        # 超时判断，若队列接受超时，将退出while循环并在输出队列put None终结队列
        try:
            data1 = input1_queue.get(timeout=2)
            data2 = input2_queue.get(timeout=2)
        except multiprocessing.queues.Empty:
            break

        if data1 is None or data2 is None:
            break

        src11, src12, src13 = code.decode(data1)
        src21, src22, src23 = code.decode(data2)
        output_queue.put(code.encode(src11, src12, src23))
    output_queue.put(None)


if __name__ == "__main__":
    start_time = time.time()
    frame_count = 0

    # 队列初始化
    line_input = multiprocessing.Queue()
    find_input = multiprocessing.Queue()
    line_output = multiprocessing.Queue()
    find_output = multiprocessing.Queue()
    combine_output = multiprocessing.Queue()

    # 进程初始化
    pl = multiprocessing.Process(target=process_line, args=(line_input, line_output))
    pf = multiprocessing.Process(target=process_find, args=(find_input, find_output))
    pc = multiprocessing.Process(target=process_combine, args=(line_output, find_output, combine_output))

    # 进程启动
    pl.start()
    pf.start()
    pc.start()

    cap = cv2.VideoCapture('../Material/pgv11.mp4')
    if not cap.isOpened():
        print("Error: Cannot open video")

    while True:
        ret, frame = cap.read()
        if not ret:
            exit()

        frame_count += 1

        # 将数据以元组形式一起发出
        data = (frame, frame_count)
        line_input.put(data)
        find_input.put(data)

        cv2.imshow('frame', frame)

        data_return = combine_output.get()

        # 避免前期接受空数据
        if frame_count > 40:
            if data_return is None:
                break

            print(f'\rframe_count: {frame_count} data_return: {code.decode(data_return)} '
                  f'{data_return:b}', end=' ')

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 进程终止
    line_input.put(None)
    find_input.put(None)

    pl.join()
    pf.join()

    line_output.put(None)
    find_output.put(None)

    pc.join()

    cap.release()
    cv2.destroyAllWindows()
