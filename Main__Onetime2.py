# -*- coding: utf-8 -*-
import numpy as np
import time
from multiprocessing import Pool

from CRC import CRC_Encoder
from Message import MessageMaker
from Encoder import Encoder
from Channel import AWGNchannel
from SCLDecoder import SCL_Decoder
from LLR_SCLDecoder import LLR_SCLDecoder
from LLR_SCLDecoder import LLR_SCDecoder
from ErrorChecker import ErrorChecker
import parameter

k = parameter.k
n = parameter.n
L = parameter.L
r = parameter.r
snr = parameter.snr
kaisu = parameter.kaisu
parallel = parameter.parallel

division_num = parameter.division_num
threshold = parameter.threshold_new

R = k/n
m = int(np.log2(n))
# K = k + r

chaneltype = "AWGN"
filepath = "./sort_I/AWGN/sort_I_AWGN_"+str(m)+"_"+str(R)+"_"+"1"+"_.dat"


if __name__ == "__main__":
    # print(x)
    ErrorChecker.ParameterCheck_multiCRC(kaisu, parallel, r, division_num)

    # メッセージの作成
    messagemaker = MessageMaker(k)
    message = messagemaker.Make()
    # print("メッセージ", message)
    
    # ポーラ符号符号化
    encoder = Encoder(k, n, filepath)
    codeword = encoder.Encode(message)
    # print("ポーラ符号語:\n",codeword)

    # 通信路
    channel = AWGNchannel(snr, k, n)
    output = channel.Transmit(codeword)
    # print("通信路出力", output)

    # LLR-SCL復号(L=1)
    llr_decoder = LLR_SCLDecoder(k, n, L, snr, filepath)
    estimated_message0 = llr_decoder.Decode(output)
    print("メッセージ推定値SCL:\n", estimated_message0)

    # LLR-SC復号
    llr_SCDecoder = LLR_SCDecoder(k, n, snr, filepath)
    estimated_message1 = llr_SCDecoder.Decode(output)
    print("メッセージ推定値SC:\n", estimated_message1)

    # フレームエラーの判定とビットエラー数の判定
    error0 = ErrorChecker.IsDecodeError(message, estimated_message0)
    error1 = ErrorChecker.IsDecodeError(message, estimated_message1)
    # print(message^estimated_message)
    print("SCL", not error0[0], error0[1])
    print("SC ", not error1[0], error1[1])

