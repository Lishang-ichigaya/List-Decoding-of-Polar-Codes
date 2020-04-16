# -*- coding: utf-8 -*-
import numpy as np
from numpy.random import rand


class MessageMaker:
    def __init__(self, K, p=0.5):
        """
        メッセージを作成するパラメータを初期化する。\n 
        K: メッセージの長さ\n
        p=0.5: 0の生成確率
        """
        self.K = K
        self.p = p

    def Make(self):
        """
        メッセージを作成する
        戻り値: {0,1}からなるメッセージ
        """
        tmprand = rand(self.K) #[0,1]∈R の一様乱数
        message = np.zeros([self.K], dtype=np.uint8)
        message[np.where(self.p < tmprand)] = 1 #乱数がp以上のビットは1にする
        return message
