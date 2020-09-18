# -*- coding: utf-8 -*-
import numpy as np
import time
from multiprocessing import Pool
from tqdm import tqdm

from CRC import CRC_Encoder
from Message import MessageMaker
from Encoder import Encoder
from Channel import AWGNchannel
from SCLDecoder import multiCRC_SCL_Decoder
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
# 区切り位置は「メッセージ」の区切り位置である

R = k/n
m = int(np.log2(n))
# K = k + r

chaneltype = "AWGN"
filepath = "./sort_I/AWGN/sort_I_AWGN_"+str(m)+"_"+str(R)+"_"+"1"+"_.dat"


def Simulation(i):
    ErrorChecker.ParameterCheck_multiCRC(kaisu, parallel, r, division_num)

    # メッセージの作成
    messagemaker = MessageMaker(k)
    message = messagemaker.Make()
    divided_message = [message[:threshold[0][0]+1-r//division_num],
                       message[threshold[0][0]+1-r//division_num:]]
    # divided_message = [message[:threshold[0][0]+1-r//division_num], message[threshold[0][0]+1-r//division_num:threshold[0][1]+1-r//division_num],
    #                    message[threshold[0][1]+1-r//division_num:threshold[0][2]+1-r//division_num], message[threshold[0][2]+1-r//division_num:]]
    # print([len(divided_message[i]) for i in range(division_num)])

    # CRC符号化
    crc_encoder = [CRC_Encoder(divided_message[i], r//division_num)
                   for i in range(division_num)]
    crc_codeword = [crc_encoder[i].Encode() for i in range(division_num)]
    concatenated_crc_codeword = np.concatenate(crc_codeword)

    # ポーラ符号符号化
    encoder = Encoder(k + r, n, filepath)
    codeword = encoder.Encode(concatenated_crc_codeword)

    # 通信路
    channel = AWGNchannel(snr, k, n)
    output = channel.Transmit(codeword)

    # CRC aided SCL復号
    decoder = multiCRC_SCL_Decoder(k, n, L, r, threshold, snr, filepath)
    estimated_message = decoder.Decode(output)

    # フレームエラーの判定とビットエラー数の判定
    error = ErrorChecker.IsDecodeError(message, estimated_message)

    error0 = error[0]
    error1 = error[1]
    error_h = ErrorChecker.IsDecodeError(
        message[:threshold[0][0]+1-r//division_num], estimated_message[:threshold[0][0]+1-r//division_num])[0]
    error_t = ErrorChecker.IsDecodeError(
        message[threshold[0][0]+1-r//division_num:], estimated_message[threshold[0][0]+1-r//division_num:])[0]
    # print(error_h, error_t)

    # if i % 20 == 0:
    #     print(i, "/", kaisu//parallel, ",", error)
    # return = error
    return error0, error1, error_h, error_t


def Simulation_wrapper(num):
    frameerrorsum = 0
    biterrorsum = 0
    np.random.seed(int(time.time()) + num)

    h_fer = 0
    t_fer = 0

    for i in tqdm(range(kaisu//parallel), desc='{0: 03d}'.format(num), leave=False):
        result = Simulation(i)
        frameerrorsum += result[0]
        biterrorsum += result[1]
        h_fer += result[2]
        t_fer += result[3]

    # print(h_fer, t_fer)
    return frameerrorsum, biterrorsum, h_fer, t_fer


if __name__ == "__main__":
    p = Pool(parallel)
    result = p.imap_unordered(Simulation_wrapper, range(parallel))

    frameerror = 0
    biterror = 0

    h_fer = 0
    t_fer = 0

    start = time.time()
    for result_i in result:
        frameerror += result_i[0]
        biterror += result_i[1]
        h_fer += result_i[2]
        t_fer += result_i[3]
    end = time.time()
    p.close()

    print("K="+str(k)+", N="+str(n) + ", L=" +
          str(L)+", r="+str(r)+", snr="+str(snr))
    print("回数: "+str(kaisu)+", フレームエラー数" + str(frameerror))
    print("FER: " + str(frameerror/kaisu))
    print("BER: " + str(biterror/(k*kaisu)))
    print("サブブロックごとのFE数: H.{}, T.{}".format(h_fer, t_fer))
    print("実行時間: " + str(end-start))
