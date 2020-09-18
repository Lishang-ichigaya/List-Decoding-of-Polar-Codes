import numpy as np
from numpy.random import rand
from numpy.random import normal

class AWGNchannel:
    def __init__(self, snr, k, n):
        """
        AWGNチャネルの初期化。\n
        snr: ビットあたりのSN比（E_b/N_0)\n
        k, n: メッセージ長、符号帳\n
        """
        self.N_0 = 10**(-snr/10)/(2*(k/n))
    
    def Transmit(self, _input):
        n = np.size(_input)
        chanel_input = np.array([+1.0 if u_i == 0 else -1.0 for u_i in _input])
        gauss_nose = normal(0, np.sqrt(self.N_0), n)
        chanel_output = chanel_input + gauss_nose
        return chanel_output

class BSC:
    def __init__(self, p):
        self.p = p
    
    def Transmit(self, _input):
        n = np.size(_input)
        noise = rand(n)
        binnoise = np.zeros([n], dtype=np.uint8)
        binnoise[np.where(self.p > noise)] = 1
        output = (_input + binnoise) % 2
        return output
