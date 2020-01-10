import numpy as np
from numpy.random import rand
import time


class Message:
    def __init__(self, K):
        """
        メッセージの初期化 
        K:メッセージの長さ
        """
        self.K = K
        # メッセージのビット数
        self.message = np.zeros(K, dtype=np.uint8)
        # メッセージ

    def MakeMessage(self, P=0.5):
        """
        メッセージの作成
        P=0.5:1の出現確率
        """
        tmprand = rand(self.K)
        message = np.zeros([self.K], dtype=np.uint8)
        message[np.where(P > tmprand)] = 1
        self.message = message


class HatMessage(Message):
    # メッセージの推定値をを保持するクラス。名前だけ変えた。
    pass


if __name__ == "__main__":
    K = 512
    sum = 0
    kaisu = 10000

    start = time.time()
    for i in range(kaisu):
        message = Message(K)
        message.MakeMessage(0.8)
        sum += np.count_nonzero(message.message)
        #print(message.message)
    end = time.time()
    print("実行時間", end-start)
    print("1の出現確率", sum/(K*kaisu))
