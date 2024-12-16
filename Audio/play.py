import pygame
import threading

file = 'Audio/doorbell.mp3'

def play_audio_blocking(audio_file=file):
    """
    在新线程中播放音频文件，并在播放完毕后返回。
    :param audio_file: 音频文件的路径
    """
    # 初始化pygame
    pygame.mixer.init()

    # 加载音频文件
    pygame.mixer.music.load(audio_file)

    # 播放音频
    pygame.mixer.music.play()

    # 等待音频播放完毕
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    # 退出pygame mixer
    pygame.mixer.quit()

def play_audio_non_blocking(audio_file=file):
    """
    在新线程中播放音频文件，不会阻塞主程序。
    :param audio_file: 音频文件的路径
    """
    # 创建并启动线程来播放音频
    audio_thread = threading.Thread(target=play_audio_blocking, args=(audio_file,))
    audio_thread.start()
