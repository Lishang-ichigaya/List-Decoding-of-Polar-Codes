# -*- coding: utf-8 -*-
from subprocess import check_call
import numpy as np
from scipy.stats import norm
import sys
import time
from matplotlib import pyplot
#from tkinter import messagebox

from message import Message
from Encoder import Encoder
from chanel import AWGN
from Decoder_awgn import ListDecoder
# from CRC import CRC_Encoder
# from CRC import CRC_Detector


if __name__ == '__main__':
    k = 128
    N = 256
    L = 1
    M = int(np.log2(N))
    chaneltype = "AWGN"
    snr = 3
    R = k/N
    P = norm.cdf(0, 1, np.sqrt(10**(-snr/10)/(2*R)))
    path = "./sort_I/"+chaneltype+"/sort_I_"+chaneltype+"_"+str(M)+"_"+str(R)+"_"+str(snr)+"_.dat"

    print("k=", k, "N=", N, "L=", L, "P=",P)

    out = []
    message = Message(k)
    message.MakeMessage()
    print("メッセージ:\t\t", message.message)

    # crcenc = CRC_Encoder(message.message, r)
    # crcenc.Encode()
    # print("CRC付与:\t\t", crcenc.codeword)

    encoder0 = Encoder(k, N, message.message, path, False)
    encoder0.MakeCodeworde()
    print("符号語:\t\t\t", encoder0.codeword)

    awgn = AWGN(snr, R)
    awgn.input = encoder0.codeword
    awgn.Transmission()
    output = awgn.output
    print("通信路出力:\t\t", output)

    decoder1 = ListDecoder(k, N, L, output, chaneltype, path, False)
    variance = 10**(-snr/10)/(2*R)
    decoder1.DecodeMessage(snr, R)
    decoded_message = decoder1.hat_message
    print("SCLメッセージ推定値:\t", decoded_message)

    error1 = np.bitwise_xor(message.message, decoded_message)
    print("SCL誤り数:", np.count_nonzero(error1))
