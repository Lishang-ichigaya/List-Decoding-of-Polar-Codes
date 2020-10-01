import numpy as np
from scipy.stats import norm
import copy

from LLR_SCLDecoder import LLR_SCLDecoder

class PAC_Decoder(LLR_SCLDecoder):
    def __init__(self, k, n, L, c, snr, path):
        """
        受信系列を復号するクラス\n
        k: メッセージ長\n
        n: 符号長\n
        L: リストサイズ\n
        c: 畳み込みのインパルス応答\n
        snr: ビットあたりのSN比（E_b/N_0)\n
        path: インデックスを相互情報量が小さい順に並べたファイルのパス\n
        """
        super().__init__(k, n, L, snr, path)
        self.c = c
    
