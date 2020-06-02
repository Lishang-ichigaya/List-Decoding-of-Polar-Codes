# -*- coding: utf-8 -*-
import numpy as np
import time
from multiprocessing import Pool

from Message import MessageMaker
from Encoder import Encoder
from Channel import AWGNchannel
from SCLDecoder import SCL_Decoder
from ErrorChecker import ErrorChecker

k = 512
n = 1024
L = 1
# r = 0 
snr = 3
kaisu = 10*10
parallel = 10 

R = k/n
m = int(np.log2(n))
# K = k + r

chaneltype = "AWGN"
filepath = "./sort_I/AWGN/sort_I_AWGN_"+str(m)+"_"+str(R)+"_"+"0"+"_.dat"

if __name__ == "__main__":
    # メッセージの作成
    messagemaker = MessageMaker(k)
    message = messagemaker.Make()
    print(message)

    # ポーラ符号符号化
    encoder = Encoder(k, n, filepath)
    codeword = encoder.Encode(message)
    print(codeword)

    # 通信路
    channel = AWGNchannel(snr, k, n)
    output = channel.Transmit(codeword)
    print(output)

    # ポーラ符号復号化
    decoder = SCL_Decoder(k, n, L, snr, filepath)
    estimated_message = decoder.Decode(output)
    print(estimated_message)

    # フレームエラーの判定とビットエラー数の判定
    error = ErrorChecker.IsDecodeError(message, estimated_message)
    print(error)

    print()
