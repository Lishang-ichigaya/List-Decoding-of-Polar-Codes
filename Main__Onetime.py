# -*- coding: utf-8 -*-
import numpy as np
import time
from multiprocessing import Pool

from CRC import CRC_Encoder
from Message import MessageMaker
from Encoder import Encoder
from Channel import AWGNchannel
from SCLDecoder import multiCRC_SCL_Decoder
from ErrorChecker import ErrorChecker

k = 128
n = 256
L = 4
r = 6 
snr = 2
kaisu = 14*2
parallel = 14 

division_num = 2
threshold = [1, 153, 255]
threshold = [(k+r)//2, k+r]
# print("しきい:", threshold)

R = k/n
m = int(np.log2(n))
# K = k + r

chaneltype = "AWGN"
filepath = "./sort_I/AWGN/sort_I_AWGN_"+str(m)+"_"+str(R)+"_"+"1"+"_.dat"


if __name__ == "__main__":
    ErrorChecker.ParameterCheck_multiCRC(kaisu, parallel, r, division_num)

    # メッセージの作成
    messagemaker = MessageMaker(k)
    message = messagemaker.Make()
    # print("メッセージ", message)
    divided_message = np.split(message, division_num)

    #CRC符号化
    crc_encoder = [CRC_Encoder(divided_message[i], r//division_num) for i in range(division_num)]
    crc_codeword = [crc_encoder[i].Encode() for i in range(division_num)]
    concatenated_crc_codeword = np.concatenate(crc_codeword)
    # print("CRC符号語", concatenated_crc_codeword)

    # ポーラ符号符号化
    encoder = Encoder(k + r, n, filepath)
    codeword = encoder.Encode(concatenated_crc_codeword)
    # print("ポーラ符号語",codeword)

    # 通信路
    channel = AWGNchannel(snr, k, n)
    output = channel.Transmit(codeword)
    # print("通信路出力", output)

    # CRC aided SCL復号
    decoder = multiCRC_SCL_Decoder(k, n, L, r, threshold, snr, filepath)
    estimated_message = decoder.Decode(output)
    # print("メッセージ推定値", estimated_message)

    # フレームエラーの判定とビットエラー数の判定
    error = ErrorChecker.IsDecodeError(message, estimated_message)
    # print(message^estimated_message)
    print(error)
    er = error[0]

