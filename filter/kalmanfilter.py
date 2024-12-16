import numpy as np

class KalmanFilter:
    def __init__(self):
        # 状态向量 [角度]
        self.x = np.zeros((1, 1))
        # 状态转移矩阵
        self.F = np.array([[1]])
        # 观测矩阵
        self.H = np.array([[1]])
        # 过程噪声协方差
        self.Q = np.array([[0.3]])
        # 观测噪声协方差
        self.R = np.array([[0.8]])
        # 估计误差协方差
        self.P = np.array([[1]])

    def predict(self):
        # 预测状态
        self.x = self.F @ self.x
        # 更新误差协方差
        self.P = self.F @ self.P @ self.F.T + self.Q

    def update(self, z):
        # 计算卡尔曼增益
        S = self.H @ self.P @ self.H.T + self.R
        K = self.P @ self.H.T @ np.linalg.inv(S)

        # 更新估计
        self.x = self.x + K @ (z - self.H @ self.x)
        # 更新误差协方差
        self.P = (np.eye(len(K)) - K @ self.H) @ self.P
