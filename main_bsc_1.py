from subprocess import check_call
import numpy as np
import sys
import time
from tkinter import messagebox

from message import Message
from Encoder import Encoder
from chanel import BSC
from Decoder import DecoderW
from Decoder import DecoderLR
from Decoder import ListDecoder
from Decoder import ListDecoder_F
from Decoder import ListDecoder_CRC
from CRC import CRC_Encoder
from CRC import CRC_Detector


if __name__ == '__main__':
    k = 128
    r = 0  # CRCの長さを変更する場合はCRC.pyも書き換える
    K = k + r
    N = 256
    L = 4
    M = int(np.log2(N))
    chaneltype = "BSC"
    P = 0.06
    path = "./sort_I/sort_I_" + str(M) + "_" + str(P) + "_" + "20" + ".dat"
    result_file_name = "samui.txt"
    # path ="./polarcode/"+"sort_I_" + str(M) + "_" + str(P) + "_" + "20" + ".dat"

    kaisu = 100
    if len(sys.argv) == 2 and sys.argv[1] == "ber":
        for P in [0.06]:
            for L in [4]:
                with open(result_file_name, mode='a', encoding='utf-8') as f:
                    f.write("-----------------------L="+str(L)+"----------------------------\n")
                for N in [128]:
                    k = N//2
                    K = k + r
                    eroorcount0 = 0
                    frameerrorcout0 = 0
                    eroorcount1 = 0
                    frameerrorcout1 = 0

                    path = path = "./sort_I/sort_I_" + str(int(np.log2(N))) + "_" + str(P) + "_" + "20" + ".dat"
                    start = time.time()
                    for i in range(kaisu):
                        message = Message(k)
                        message.MakeMessage()

                        #crcenc = CRC_Encoder(message.message)
                        #crcenc.Encode()

                        encoder0 = Encoder(K, N, message.message, path, False)
                        encoder0.MakeCodeworde()

                        bsc = BSC(P)
                        bsc.input = encoder0.codeword
                        bsc.Transmission()
                        output = bsc.output

                        # decoder0name = "_SC"
                        # start0 = time.time()
                        # decoder0 = DecoderW(K, N, output, chaneltype, path, False)
                        # decoder0.DecodeMessage(P)
                        # hat_message0 = Message(K)
                        # hat_message0.message = decoder0.hat_message
                        # end0 = time.time()

                        decoder1name = "SCL"
                        # start1 = time.time()
                        decoder1 = ListDecoder_F(K, N, L, output, chaneltype, path, False)
                        decoder1.DecodeMessage(P)
                        hat_message1 = Message(k)
                        hat_message1.message = decoder1.hat_message
                        # end1 = time.time()

                        # error0 = np.bitwise_xor(message.message, hat_message0.message)
                        error1 = np.bitwise_xor(message.message, hat_message1.message)

                        # eroorcount0 += np.count_nonzero(error0)
                        eroorcount1 += np.count_nonzero(error1)

                        # frameerrorcout0 += 0 if np.count_nonzero(error0) == 0 else 1
                        frameerrorcout1 += 0 if np.count_nonzero(error1) == 0 else 1
                        print(i, "/", kaisu, "回目, ",
                              #       0 if np.count_nonzero(error0) == 0 else 1,
                              0 if np.count_nonzero(error1) == 0 else 1)
                        # print("FSCL:", "{0:.5f}".format(end0-start0), "SCL", "{0:.5f}".format(end1-start1))
                    end = time.time()

                    if True:
                        with open(result_file_name, mode='a', encoding='utf-8') as f:
                            f.write("K="+str(K)+", N="+str(N) + ", r=" + str(r) + ", L="+str(L)+", P="+str(P)+"\n")
                            # f.write("送信メッセージ数: " + str(K*kaisu)+", " + decoder0name + "復号誤り: "
                            #       + str(eroorcount0)+", " + decoder1name + "復号誤り: " + str(eroorcount1))
                            f.write("送信メッセージ数: " + str(K*kaisu)+", " + decoder1name + "復号誤り: " + str(eroorcount1)+"\n")
                            #f.write("FER_" + decoder0name + ": " + str(frameerrorcout0/kaisu)+"\n")
                            f.write("FER_" + decoder1name + ": " + str(frameerrorcout1/kaisu)+"\n")
                            #f.write("BER_" + decoder0name + ": " + str(eroorcount0/(K*kaisu))+"\n")
                            f.write("BER_" + decoder1name + ": " + str(eroorcount1/(K*kaisu))+"\n")
                            f.write("実行時間: " + str(end-start)+"\n")

                    if True:
                        print("K="+str(K)+", N="+str(N) + ", r=" + str(r) + ", L="+str(L)+", P="+str(P))
                        #print("送信メッセージ数: " + str(K*kaisu)+", " + decoder0name + "復号誤り: " +
                        #      str(eroorcount0)+", " + decoder1name + "復号誤り: " + str(eroorcount1))
                        print("送信メッセージ数: " + str(K*kaisu)+", " + decoder1name + "復号誤り: " + str(eroorcount1))
                        #print("FER_" + decoder0name + ": " + str(frameerrorcout0/kaisu))
                        print("FER_" + decoder1name + ": " + str(frameerrorcout1/kaisu))
                        #print("BER_" + decoder0name + ": " + str(eroorcount0/(K*kaisu)))
                        print("BER_" + decoder1name + ": " + str(eroorcount1/(K*kaisu)))
                        print("実行時間: " + str(end-start))

    if len(sys.argv) == 1:
        print("K=", k, "N=", N, "r=", r, "L=", L)

        message = Message(k)
        message.MakeMessage()
        print("メッセージ:\t\t", message.message)

        crcenc = CRC_Encoder(message.message)
        crcenc.Encode()
        print("CRC付与:\t\t", crcenc.codeword)

        encoder0 = Encoder(K, N, crcenc.codeword, path)
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

        decoder1 = ListDecoder_CRC(K, N, L, output, chaneltype, path, False)
        decoder1.DecodeMessage(P)
        hat_message1 = Message(K)
        hat_message1.message = decoder1.hat_message[:k]
        print("CASCLメッセージ推定値:\t", hat_message1.message)

        # print("本当のメッセージ:\t", message.message)

        # error0 = np.bitwise_xor(message.message, hat_message0.message)
        # print("  SCL誤り数:", np.count_nonzero(error0))
        error1 = np.bitwise_xor(message.message, hat_message1.message)
        print("CASCL誤り数:", np.count_nonzero(error1))
