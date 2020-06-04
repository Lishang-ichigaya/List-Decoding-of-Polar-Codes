# -*- coding: utf-8 -*-
import numpy as np
import time
from multiprocessing import Pool

from CRC import CRC_Encoder
from Message import MessageMaker
from Encoder import Encoder
from Channel import BSC
from SCLDecoder import SCL_Decoder_BSC
from ErrorChecker import ErrorChecker
import parameter

k = parameter.k
n = parameter.n
L = parameter.L
p = parameter.p
kaisu = parameter.kaisu
parallel = parameter.parallel

R = k/n
m = int(np.log2(n))
# K = k + r

chaneltype = "BSC"
filepath = "./sort_I/BSC/sort_I_"+str(m)+"_"+str(p)+".dat"


if __name__ == "__main__":
    # メッセージの作成
    messagemaker = MessageMaker(k)
    message = messagemaker.Make()

    # ポーラ符号符号化
    polar_encoder = Encoder(k, n, filepath)
    codeword = polar_encoder.Encode(message)

    # 通信路
    channel = BSC(p)
    output = channel.Transmit(codeword)

    # CRC aided SCL復号
    decoder = SCL_Decoder_BSC(k, n, L, p, filepath)
    estimated_message = decoder.Decode(output)

    # フレームエラーの判定とビットエラー数の判定
    error = ErrorChecker.IsDecodeError(message, estimated_message)

    # if i % 10 == 0:
    #     print(i, "/", kaisu//parallel, ",", error)
    print(error)
    er = error[0]

