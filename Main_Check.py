# -*- coding: utf-8 -*-
import numpy as np
import time
from multiprocessing import Pool

from CRC import CRC_Encoder
from Message import MessageMaker
from Encoder import Encoder
from Channel import AWGNchannel
from SCLDecoder import CASCL_Decoder
from SCLDecoder import SCL_Decoder
from ErrorChecker import ErrorChecker

k = 256
n = 512
L = 4
r = 4
snr = 2
kaisu = 16*100
parallel = 16

R = k/n
m = int(np.log2(n))
# K = k + r

chaneltype = "AWGN"
filepath = "./sort_I/AWGN/sort_I_AWGN_"+str(m)+"_"+str(R)+"_"+"1"+"_.dat"


def Simulation(i):
    # メッセージの作成
    messagemaker = MessageMaker(k)
    message = messagemaker.Make()

    # CRC符号化
    crc_encoder = CRC_Encoder(message, r)
    crc_codeword = crc_encoder.Encode()

    # ポーラ符号符号化
    encoder = Encoder(k + r, n, filepath)
    codeword = encoder.Encode(crc_codeword)

    # 通信路
    channel = AWGNchannel(snr, k + r, n)
    output = channel.Transmit(codeword)

    # CRC aided SCL復号
    decoder_nocrc = SCL_Decoder(k+r, n, L, snr, filepath)
    estimated_message_nocrc = decoder_nocrc.Decode(output)
    estimated_message_nocrc = estimated_message_nocrc[:k]

    decoder_crc = CASCL_Decoder(k, n, L, r, snr, filepath)
    estimated_message = decoder_crc.Decode(output)


    # フレームエラーの判定とビットエラー数の判定
    error_nocrc = ErrorChecker.IsDecodeError(message, estimated_message_nocrc)
    error_crc = ErrorChecker.IsDecodeError(message, estimated_message)

    # if i % 20 == 0:
    #     print(i, "/", kaisu//parallel, ",", error)
    return error_nocrc[0],  error_nocrc[1], error_crc[0], error_crc[1]


def Simulation_wrapper(num):
    frameerrorsum_n = 0
    biterrorsum_n = 0
    frameerrorsum_c = 0
    biterrorsum_c = 0
    np.random.seed(int(time.time()) + num)

    for i in range(kaisu//parallel):
        result = Simulation(i)
        frameerrorsum_n += result[0]
        biterrorsum_n += result[1]
        frameerrorsum_c += result[2]
        biterrorsum_c += result[3]

    return [frameerrorsum_n, biterrorsum_n, frameerrorsum_c, biterrorsum_c]


if __name__ == "__main__":
    p = Pool(parallel)
    result = p.imap_unordered(Simulation_wrapper, range(parallel))

    frameerror_n = 0
    biterror_n = 0
    frameerror_c = 0
    biterror_c = 0
    start = time.time()
    for result_i in result:
        frameerror_n += result_i[0]
        biterror_n += result_i[1]
        frameerror_c += result_i[2]
        biterror_c += result_i[3]
    end = time.time()
    p.close()

    print("K="+str(k)+", N="+str(n) + ", L="+str(L)+", snr="+str(snr))
    print("回数: "+str(kaisu)+", nフレームエラー数" + str(frameerror_n) + ", cフレームエラー数", str(frameerror_c))
    print("nFER: " + str(frameerror_n/kaisu) + ", cFER: " + str(frameerror_c/kaisu))
    print("nBER: " + str(biterror_n/(k*kaisu))+ ", cBER: " + str(biterror_c/(k*kaisu)))
    print("実行時間: " + str(end-start))
