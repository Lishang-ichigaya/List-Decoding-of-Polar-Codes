from subprocess import check_call
import numpy as np
import sys
import time

from message import Message
#from codeword import CodeWorde
from Encoder import Encoder
from chanel import BEC
from Decoder import DecoderW
from Decoder import DecoderLR


if __name__ == '__main__':
    K = 8
    N = 16
    M = int(np.log2(N))
    chaneltype = "BEC"
    #e = 0.1
    kaisu = 10000

    #path = "./sort_I/sortI_BEC_"+ str(e) + "_" + str(N) + ".dat"
    # path ="./polarcode/"+"sort_I_" + str(M) + "_" + str(P) + "_" + "20" + ".dat"

    if len(sys.argv) == 2:
        if sys.argv[1] == "ber":
            for e in [0.1, 0.2, 0.3, 0.4, 0.5]:
                K = 8
                N = 16
                M = int(np.log2(N))
                if True:
                    with open("bectakusan.txt",mode='a',encoding='utf-8') as f:
                        f.write("-----------------------"+str(e)+"----------------------------\n")
                for j in range(6):
                    eroorcount0 = 0
                    frameerrorcout0 = 0
                    eroorcount1 = 0
                    frameerrorcout1 = 0
                    K *= 2
                    N *= 2
                    path = "./sort_I/sortI_BEC_"+ str(e) + "_" + str(N) + ".dat"
                    kaisu = 1000 if N==1024 else 10000
                    start = time.time()
                    for i in range(kaisu):
                        message = Message(K)
                        message.MakeMessage()

                        encoder0 = Encoder(K, N, message.message, path, False)
                        encoder0.MakeCodeworde()
                        
                        bec = BEC(e)
                        bec.input = encoder0.codeword
                        bec.Transmission()
                        output = bec.output
                    
                        #decoder0 = DecoderW(K, N ,output, chaneltype, path, False)
                        #decoder0.DecodeMessage(e)
                        #hat_message0 = Message(K)
                        #hat_message0.message = decoder0.hat_message

                        decoder1 = DecoderLR(K, N ,output, chaneltype, path, False)
                        decoder1.DecodeMessage(e)
                        hat_message1 = Message(K)
                        hat_message1.message = decoder1.hat_message

                        #error0 = np.bitwise_xor(message.message, hat_message0.message)
                        error1 = np.bitwise_xor(message.message, hat_message1.message)

                        #eroorcount0 += np.count_nonzero(error0)
                        eroorcount1 += np.count_nonzero(error1)

                        #frameerrorcout0 += 0 if np.count_nonzero(error0) == 0 else 1
                        frameerrorcout1 += 0 if np.count_nonzero(error1) == 0 else 1
                        print(i, "/", kaisu, "回目, ",
                        #    0 if np.count_nonzero(error0) == 0 else 1,
                            0 if np.count_nonzero(error1) == 0 else 1)
                    end = time.time()

                    #ファイル書き込み
                    if True:
                        with open("bectakusan.txt",mode='a',encoding='utf-8') as f:
                            f.write("K="+str(K)+", N="+str(N)+", e="+str(e)+"\n")
                            f.write("送信: "+ str(K*kaisu)+ ", W復号誤り: "+ str(eroorcount0)+"\n")
                            #f.write("FER__W: "+ str(frameerrorcout0/kaisu)+"\n")
                            f.write("FER_LR: "+ str(frameerrorcout1/kaisu)+"\n")
                           # f.write("BER__W: "+ str(eroorcount0/(K*kaisu))+"\n")
                            f.write("BER_LR: "+ str(eroorcount1/(K*kaisu))+"\n")
                            f.write("実行時間: "+ str(end-start)+"\n")
                    #表示
                    if True:
                        print("K="+str(K)+", N="+str(N), "e=",e)
                        print("送信: "+ str(K*kaisu)+ ", 復号誤り: "+ str(eroorcount1))
                        #print("FER__W: "+ str(frameerrorcout0/kaisu))
                        print("FER_LR: "+ str(frameerrorcout1/kaisu))
                        #print("BER__W: "+ str(eroorcount0/(K*kaisu)))
                        print("BER_LR: "+ str(eroorcount1/(K*kaisu)))
                        print("実行時間: "+ str(end-start))

    if len(sys.argv) == 1:
        print("K=", K, "N=", N)

        message = Message(K)
        message.MakeMessage()
        print("メッセージ:\t\t", message.message)

        encoder0 = Encoder(K, N, message.message, path)
        encoder0.MakeCodeworde()
        print("符号語:\t\t\t", encoder0.codeword)

        bec = BEC(e)
        bec.input = encoder0.codeword
        bec.Transmission()
        output = bec.output
        print("通信路出力:\t\t", output)


        #decoder0 = DecoderW(K, N ,output, chaneltype, path)
        #decoder0.DecodeMessage(e)
        #hat_message0 = Message(K)
        #hat_message0.message = decoder0.hat_message
        #print("メッセージ推定値 W:\t", hat_message0.message)

        decoder1 = DecoderLR(K, N ,output, chaneltype, path)
        decoder1.DecodeMessage(e)
        hat_message1 = Message(K)
        hat_message1.message = decoder1.hat_message
        print("メッセージ推定値LR:\t", hat_message1.message)

        #error0 = np.bitwise_xor(message.message, hat_message0.message)
        #print("誤り数 W:", np.count_nonzero(error0))
        error1 = np.bitwise_xor(message.message, hat_message1.message)
        chanelerror = np.bitwise_xor(encoder0.codeword, bec.output)
        print("通信路での誤り数:", np.count_nonzero(chanelerror) , "/", N)
        print("誤り数:", np.count_nonzero(error1))