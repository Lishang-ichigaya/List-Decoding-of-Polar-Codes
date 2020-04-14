from Decoder_awgn import ListDecoder
from chanel import AWGN
from Encoder import Encoder
from message import Message
from multiprocessing import Pool
import numpy as np
from scipy.stats import norm
import time
import sys
sys.path.append("/Users/pikac/Documents/MyPyLibrary")
import notification

k = 128
N = 256
L = 1
r = 0  # CRCの長さ
snr = 2
kaisu = 40
parallelnum = 4 

R = k/N
P = norm.cdf(0, 1, np.sqrt(10**(-snr/10)/(2*R)))
M = int(np.log2(N))
# K = k + r
threshold = 0  # CRCの区切り位置
threshold_m = threshold - r//2  # メッセージの区切り位置
SaveResult = False
SaveLog = False
decodername = "SCL"

chaneltype = "AWGN"
path = "./sort_I/"+chaneltype+"/sort_I_"+chaneltype+"_"+str(M)+"_"+str(R)+"_"+str(snr)+"_.dat"
result_file_name = "./re/"+str(N)+"_"+str(P)+"_"+str(kaisu)+decodername+".txt"


def Simulation(i):
    # メッセージの作成
    message = Message(k)
    message.MakeMessage()

    # # CRC符号化
    # crcenc0 = CRC_Encoder(message.message[:threshold_m], r//2)
    # crcenc0.Encode()
    # crcenc1 = CRC_Encoder(message.message[threshold_m:], r//2)
    # crcenc1.Encode()
    # crccodeword = np.concatenate([crcenc0.codeword, crcenc1.codeword])

    # ポーラ符号符号化
    encoder0 = Encoder(k, N, message.message, path, False)
    encoder0.MakeCodeworde()

    # 通信路
    awgn = AWGN(snr, R)
    awgn.input = encoder0.codeword
    awgn.Transmission()
    output = awgn.output

    # ポーラ符号復号化
    decoder1 = ListDecoder(k, N, L, output, chaneltype, path, False)
    decoder1.DecodeMessage(snr, R)
    decoded_message = decoder1.hat_message

    # # メッセージの取り出し
    # hat_message = np.delete(decoder1.hat_message, np.s_[threshold-r//2:threshold], 0)
    # hat_message = np.delete(hat_message, np.s_[k:], 0)

    # フレームエラーの判定とビットエラー数の判定
    error1 = np.bitwise_xor(message.message, decoded_message)
    biterror = np.count_nonzero(error1)
    frameerror = 0 if biterror == 0 else 1
    if i %10 == 0:
        print(i, "/", kaisu//parallelnum, ",", frameerror)
    return [frameerror, biterror]


def Simulation_wrapper(num):
    frameerrorsum = 0
    biterrorsum = 0
    np.random.seed(int(time.time()) + num)
    
    for i in range(kaisu//parallelnum):
        result = Simulation(i)
        frameerrorsum += result[0]
        biterrorsum += result[1]
        if SaveLog:
            if i%100 == 0:
                with open(result_file_name+".log", mode="a", encoding="utf-8") as log:
                    log.write(str(num)+","+str(frameerrorsum)+","+str(i)+"\n")

    return [frameerrorsum, biterrorsum]


if __name__ == '__main__':
    p = Pool(parallelnum)
    result = p.imap_unordered(Simulation_wrapper, range(parallelnum))
    
    frameerror = 0
    biterror = 0
    start = time.time()
    for result_i in result:
        frameerror += result_i[0]
        biterror += result_i[1]
    end = time.time()
    p.close()

    frameerrorcout = frameerror
    biteroorcount = biterror
    if SaveResult:
        with open(result_file_name, mode='a', encoding='utf-8') as f:
            f.write("K="+str(k)+", N="+str(N) + ", r=" + str(r) +
                    ", threshold="+str(threshold)+", L="+str(L)+", P="+str(P)+"\n")
            f.write("回数: "+str(kaisu)+", 送信メッセージ数: " + str(k*kaisu)+", " + decodername +
                    ", フレームエラー数" + str(frameerrorcout)+", ビットエラー数: " + str(biteroorcount)+"\n")
            f.write("FER_" + decodername + ": " + str(frameerrorcout/kaisu)+"\n")
            f.write("BER_" + decodername + ": " + str(biteroorcount/(k*kaisu))+"\n")
            f.write("実行時間: " + str(end-start)+"\n")

    print(decodername)
    print("K="+str(k)+", N="+str(N) + ", r=" + str(r) +
        ", threshold="+str(threshold)+", L="+str(L)+", P="+str(P))
    print("回数: "+str(kaisu)+", 送信メッセージ数: " + str(k*kaisu)+", " + decodername +
        ", フレームエラー数" + str(frameerrorcout)+", ビットエラー数: " + str(biteroorcount))
    print("FER_" + decodername + ": " + str(frameerrorcout/kaisu))
    print("BER_" + decodername + ": " + str(biteroorcount/(k*kaisu)))
    print("実行時間: " + str(end-start))

    try:
        notification.LineNoticeTermination()
    except:
        print("notification error")
