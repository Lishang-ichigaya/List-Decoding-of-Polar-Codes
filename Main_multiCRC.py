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
threshold = parameter.threshold
#区切り位置は「メッセージ」の区切り位置である

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
    divided_message = np.split(message, division_num)

    #CRC符号化
    crc_encoder = [CRC_Encoder(divided_message[i], r//division_num) for i in range(division_num)]
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

    # if i % 20 == 0:
    #     print(i, "/", kaisu//parallel, ",", error)
    return error


def Simulation_wrapper(num):
    frameerrorsum = 0
    biterrorsum = 0
    np.random.seed(int(time.time()) + num)

    for i in tqdm(range(kaisu//parallel), desc='{0: 03d}'.format(num), leave=False):
        result = Simulation(i)
        frameerrorsum += result[0]
        biterrorsum += result[1]

    return [frameerrorsum, biterrorsum]

if __name__ == "__main__":
    p = Pool(parallel)
    result = p.imap_unordered(Simulation_wrapper, range(parallel)) 

    frameerror = 0
    biterror = 0
    start = time.time()
    for result_i in result:
        frameerror += result_i[0]
        biterror += result_i[1]
    end = time.time()
    p.close()

    print("K="+str(k)+", N="+str(n) +", L="+str(L)+", r="+str(r)+", snr="+str(snr))
    print("回数: "+str(kaisu)+", フレームエラー数" + str(frameerror))
    print("FER: " + str(frameerror/kaisu))
    print("BER: " + str(biterror/(k*kaisu)))
    print("実行時間: " + str(end-start))
