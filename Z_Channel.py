import numpy as np
from numpy.random import rand
from numpy.random import normal

class AWGNchannel:
    def __init__(self, snr, R):
        """
        AWGNチャネルの初期化。\n
        snr: ビットあたりのSN比（E_b/N_0).  R: 符号化レート\n
        """
        self.N_0 = 10**(-snr/10)/(2*R)
    
    def Transmit(self, _input):
        n = np.size(_input)
        chanel_input = np.array([+1.0 if u_i == 0 else -1.0 for u_i in _input])
        gauss_nose = normal(0, np.sqrt(self.N_0), n)
        chanel_output = chanel_input + gauss_nose
        return chanel_output

