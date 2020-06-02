# -*- coding: utf-8 -*-
import numpy as np
import time
from multiprocessing import Pool

from CRC import CRC_Encoder
from Message import MessageMaker
from Encoder import Encoder
from Channel import AWGNchannel
from SCLDecoder import CASCL_Decoder
from ErrorChecker import ErrorChecker

k = 256
n = 512
L = 1
r = 4 
snr = 2
kaisu = 14*2
parallel = 14 

R = k/n
m = int(np.log2(n))
# K = k + r

chaneltype = "AWGN"
filepath = "./sort_I/AWGN/sort_I_AWGN_"+str(m)+"_"+str(R)+"_"+"1"+"_.dat"


if __name__ == "__main__":
    # メッセージの作成
    messagemaker = MessageMaker(k)
    message = messagemaker.Make()
    # print("メッセージ", message)

    #CRC符号化
    crc_encoder = CRC_Encoder(message, r)
    crc_codeword = crc_encoder.Encode()
    # print("CRC符号語", crc_codeword)

    # ポーラ符号符号化
    encoder = Encoder(k + r, n, filepath)
    codeword = encoder.Encode(crc_codeword)
    # print("ポーラ符号語",codeword)

    # 通信路
    channel = AWGNchannel(snr, k, n)
    output = channel.Transmit(codeword)
    # print("通信路出力", output)

    # CRC aided SCL復号
    decoder = CASCL_Decoder(k, n, L, r, snr, filepath)
    estimated_message = decoder.Decode(output)
    # print("メッセージ推定値", estimated_message)

    # フレームエラーの判定とビットエラー数の判定
    error = ErrorChecker.IsDecodeError(message, estimated_message)
    # print(message^estimated_message)
    print("誤り", error)
