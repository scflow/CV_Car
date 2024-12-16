import pygame

# 初始化pygame
pygame.init()

# 加载音频文件
pygame.mixer.music.load('doorbell.mp3')

# 播放音频
pygame.mixer.music.play()

# 保持程序运行，直到音频播放完毕
while pygame.mixer.music.get_busy():
    pygame.time.Clock().tick(10)
