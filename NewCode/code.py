from ctypes import c_int


def decode(src):
    c_src = c_int(src)
    # 先将 c_int 实例转换为普通整数，再进行算术运算
    des1 = c_src.value // 1024
    des2 = (c_src.value // 32) % 32
    des3 = c_src.value % 32
    return des1, des2, des3


def encode(src1, src2, src3):
    c_src1 = c_int(src1)
    c_src2 = c_int(src2)
    c_src3 = c_int(src3)
    # 直接使用 c_int 实例进行算术运算
    return c_src1.value * 1024 + c_src2.value * 32 + c_src3.value
