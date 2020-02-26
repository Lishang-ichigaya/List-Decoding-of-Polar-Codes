#from subprocess import check_call
from CRC import CRC_Detector
from CRC import CRC_Encoder
from Decoder import ListDecoder_TwoCRC
from Decoder import ListDecoder_CRC
from Decoder import ListDecoder_F
from chanel import BSC
from chanel import BEC
from Encoder import Encoder
from message import Message
import time
from multiprocessing import Pool
import sys
import numpy as np
np.set_printoptions(linewidth=100)

#from Decoder import DecoderW
# from Decoder import DecoderLR
#from Decoder import ListDecoder


k = 256
N = 512
r = 6  # CRCの長さ
P = 0.09   #for文で変えます
kaisu = 100 #for文で変えます
L = 4
K = k + r
threshold = K//2  # CRCの区切り位置
SaveResult = False
SaveLog = False
decodername = "SCTest"

M = int(np.log2(N))
threshold_m = threshold - r//2  # メッセージの区切り位置
chaneltype = "BSC"
path = "./sort_I/" + chaneltype + "/sort_I_" + str(M) + "_" + str(P) + ".dat"
# path = "./sort_I/sortI_BEC_" + str(P) + "_" + str(N) + ".dat"
result_file_name = "./re/"+str(N)+"_"+str(P)+"_"+str(kaisu)+decodername+".txt"
parallelnum = 4

def Simulation(i):
    # メッセージの作成
    message = Message(k)
    message.MakeMessage()

    # CRC符号化
    crcenc0 = CRC_Encoder(message.message[:threshold_m], r//2)
    crcenc0.Encode()
    crcenc1 = CRC_Encoder(message.message[threshold_m:], r//2)
    crcenc1.Encode()
    crccodeword = np.concatenate([crcenc0.codeword, crcenc1.codeword])

    # ポーラ符号符号化
    encoder0 = Encoder(K, N, crccodeword, path, False)
    encoder0.MakeCodeworde()

    # 通信路
    bsc = BSC(P)
    bsc.input = encoder0.codeword
    bsc.Transmission()
    output = bsc.output

    # ポーラ符号とCRC復号化
    decoder1 = ListDecoder_TwoCRC(K, N, L, r, threshold, output, chaneltype, path, False)
    decoder1.DecodeMessage(P)

    # メッセージの取り出し
    hat_message = np.delete(decoder1.hat_message, np.s_[threshold-r//2:threshold], 0)
    hat_message = np.delete(hat_message, np.s_[k:], 0)

    # フレームエラーの判定とビットエラー数の判定
    error1 = np.bitwise_xor(message.message, hat_message)
    biterror = np.count_nonzero(error1)
    frameerror = 0 if biterror == 0 else 1
    if i % 20 == 0:
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
    if len(sys.argv) == 2 and sys.argv[1] == "ber":
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
