import numpy as np
import time
from multiprocessing import Pool
from numpy.random import rand
from scipy.stats import norm

from chanel import AWGN

if __name__ == "__main__":
    K = 300000
    snr = 3
    R = 0.5

    tmprand = rand(K)
    message = np.zeros([K], dtype=np.uint8)
    message[np.where(0.5 > tmprand)] = 1

    channel = AWGN(snr, R)
    channel.input = message
    output = channel.Transmission()
    bpsk_decode = np.array([0 if y >0 else 1 for y in output])

    error = np.bitwise_xor(message, bpsk_decode)
    print(np.count_nonzero(error)/K, norm.cdf(0, 1, np.sqrt(10**(-snr/10)/(2*R))))





