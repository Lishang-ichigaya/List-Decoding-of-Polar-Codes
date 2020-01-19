#from subprocess import check_call
from CRC import CRC_Detector
from CRC import CRC_Encoder
from Decoder import ListDecoder_TwoCRCfair
from Decoder import ListDecoder_TwoCRC
from Decoder import ListDecoder_CRC
from Decoder import ListDecoder_F
from chanel import BSC
from Encoder import Encoder
from message import Message
import time
from multiprocessing import Pool
import sys
import numpy as np
np.set_printoptions(linewidth=100)

#from Decoder import DecoderW
#from Decoder import DecoderLR
#from Decoder import ListDecoder


k = 128
r = 6  # CRCの長さ
threshold = 48  # CRCの区切り位置
threshold_m = threshold - r//2  # メッセージの区切り位置
K = k + r
N = 256
L = 4
M = int(np.log2(N))
chaneltype = "BSC"
P = 0.06
path = "./sort_I/sort_I_" + str(M) + "_" + str(P) + "_" + "20" + ".dat"
kaisu = 200000
decodername = "TwoUnfairCRC"
is_record_log = True
result_file_name = "ZA_TwoUnfairCRC.txt"

def OneProcess(i):

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
    decoder1 = ListDecoder_CRC(K, N, L, r, output, chaneltype, path, False)
    decoder1.DecodeMessage(P)

    # メッセージの取り出し
    hat_message = np.delete(decoder1.hat_message, np.s_[threshold-r//2:threshold], 0)
    hat_message = np.delete(hat_message, np.s_[k:], 0)

    # フレームエラーの判定とビットエラー数の判定
    error1 = np.bitwise_xor(message.message, hat_message)
    biterror = np.count_nonzero(error1)
    frameerror = 0 if np.count_nonzero(error1) == 0 else 1
    print(i, "/", kaisu, "回目, ", frameerror)
    with open(result_file_name+".log", mode="a", encoding="utf-8") as log:
        log.write(str(i)+", "+str(frameerror)+","+str(biterror)+"\n")

    return [frameerror, biterror]


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == "ber":        
        # if is_record_log:
        #     with open(result_file_name, mode='a', encoding='utf-8') as f:
        #         f.write("-----------------------P="+str(P)+"----------------------------\n")

        frameerror = []
        biterror = []
        p = Pool(4)
        result = p.imap_unordered(OneProcess, range(kaisu))
        
        start = time.time()
        for result_i in result:
            frameerror.append(result_i[0])
            biterror.append(result_i[1])
        end = time.time()
        p.close()

        frameerrorcout = sum(frameerror)
        biteroorcount = sum(biterror)
        if is_record_log:
            with open(result_file_name, mode='a', encoding='utf-8') as f:
                f.write("K="+str(k)+", N="+str(N) + ", r=" + str(r) + ", threshold="+str(threshold)+", L="+str(L)+", P="+str(P)+"\n")
                f.write("回数: "+str(kaisu)+", 送信メッセージ数: " + str(k*kaisu)+", " + decodername +
                        ", フレームエラー数" + str(frameerrorcout)+", ビットエラー数: " + str(biteroorcount)+"\n")  
                f.write("FER_" + decodername + ": " + str(frameerrorcout/kaisu)+"\n")
                f.write("BER_" + decodername + ": " + str(biteroorcount/(k*kaisu))+"\n")
                f.write("実行時間: " + str(end-start)+"\n")

        print(decodername)
        print("K="+str(k)+", N="+str(N) + ", r=" + str(r) + ", threshold="+str(threshold)+", L="+str(L)+", P="+str(P))
        print("回数: "+str(kaisu)+", 送信メッセージ数: " + str(k*kaisu)+", " + ", フレームエラー数" + str(frameerrorcout)+", ビットエラー数: " + str(biteroorcount))
        print("FER_" + decodername + ": " + str(frameerrorcout/kaisu))
        print("BER_" + decodername + ": " + str(biteroorcount/(k*kaisu)))
        print("実行時間: " + str(end-start))

    if len(sys.argv) == 1:
        print("k=", k, "N=", N, "r=", r, "L=", L)

        message = Message(k)
        message.MakeMessage()
        print("メッセージ:\t\t", message.message)

        crcenc0 = CRC_Encoder(message.message, r)
        crcenc0.Encode()
        crccodeword = crcenc0.codeword
        print("CRC付与:\t\t", crccodeword)

        encoder0 = Encoder(K, N, crccodeword, path)
        encoder0.MakeCodeworde()
        print("符号語:\t\t\t", encoder0.codeword)

        bsc = BSC(P)
        bsc.input = encoder0.codeword
        bsc.Transmission()
        output = bsc.output
        print("通信路出力:\t\t", output)

        # decoder0 = ListDecoder_F(K, N, L, output, chaneltype, path, False)
        # decoder0.DecodeMessage(P)
        # hat_message0 = Message(K)
        # hat_message0.message = decoder0.hat_message
        # print("  SCLメッセージ推定値:\t", hat_message1.message)

        decoder1 = ListDecoder_CRC(K, N, L, r, output, chaneltype, path, False)
        decoder1.DecodeMessage(P)
        hat_message1 = Message(K)
        hat_message1.message = decoder1.hat_message
        print("CRC付与推定値\t\t", hat_message1.message)
        hat_message = np.delete(hat_message1.message, np.s_[k:], 0)
        print("CASCLメッセージ推定値:\t", hat_message)

        # print("本当のメッセージ:\t", message.message)

        # error0 = np.bitwise_xor(message.message, hat_message0.message)
        # print("  SCL誤り数:", np.count_nonzero(error0))
        error1 = np.bitwise_xor(message.message, hat_message)
        print("CASCL誤り数:", np.count_nonzero(error1))
