import sys
import termios
import tty
import control

def read_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())  # 设置终端为原始模式
        while True:
            ch = sys.stdin.read(1)  # 读取一个字符
            if ch == '\x1b':  
                # 读取下一个字符
                ch1 = sys.stdin.read(1)
                if ch1 == '[':
                    # 读取下一个字符
                    ch2 = sys.stdin.read(1)
                    if ch2 in 'ABCD':
                        return {'A': 'up', 'B': 'down', 'C': 'right', 'D': 'left'}.get(ch2, None)
            elif ch in 'wasd':  # 检查是否是wasd键
                return ch
            elif ch == 'q':  # 检查是否是退出键
                return 'q'
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)  # 恢复终端设置


def main():
    x, y, z, w = 90, 0, 90, 98  # 初始位置，四个维度

    print("Use the 'wasd' or arrow keys to move in four dimensions. Press 'q' to quit.")

    while True:

        key = read_key()
        if key == 'up':
            if y < 7:
                y += 3
        elif key == 'down':
            if y > -7:
                y -= 3
        elif key == 'left':
            if x < 110:
                x += 5
        elif key == 'right':
            if x > 70:
                x -= 5
        elif key == 'q':  # 按'q'退出程序
            print('\nFinish!')
            control.pigpio_stop()
            break
        elif key == 'a':
            z -= 1
        elif key == 'd':
            z += 1
        elif key == 's':
            w -= 1
        elif key == 'w':
            w += 1

        print(f"\rCurrent position: (\t{x},\t{y},\t{z},\t{w})", end='')
        control.servo.set_angle(x)
        control.motor.set_speed(y)
        control.gimbal_x.set_angle(z)
        control.gimbal_y.set_angle(w)
if __name__ == "__main__":
    main()