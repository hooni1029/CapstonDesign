import os
from socket import *
import threading
import socket
import glob
import random
from time import sleep
import cv2
import struct
import pickle
import cv2
import time
import numpy as np

IP = '192.168.0.17'
PORT = 6025
ADDR = (IP, PORT)
SIZE = 4096

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
writer1 = cv2.VideoWriter('./file1.mp4', fourcc, 24, (1080,1920))
writer2 = cv2.VideoWriter('./file2.mp4', fourcc, 24, (1080,1920))
mk = True
c0 = False
c1 = False
def handle_client(conn, addr):
    data_buffer1 = b""
    data_buffer2 = b""
    data_size = struct.calcsize("L")
    global mk
    global c0
    global c1
    while (c0==False) or (c1==False):
        print("프레임 1개 전송")
        lock.acquire()
        time.sleep(0.33)
        if mk == True: #어떤 thread가 전송할지 mk로 표현
            print("전송 : 프레임1")
            while len(data_buffer1) < data_size:
                data_buffer1 += conn.recv(SIZE) #보낼 data를 data_buffer에 넣고
                if len(data_buffer1) == 0: #보낼게 없으면
                    print("보낼 프레임1 없음")
                    c0 = True #다 전송했다고 알리기 위해 변수 c0를 True로 변경
                    lock.release()
                    break
            if c0 == False: #보낼게 있으면
                packed_data_size1 = data_buffer1[:data_size]
                data_buffer1 = data_buffer1[data_size:]

                frame_size1 = struct.unpack(">L", packed_data_size1)[0]

                while len(data_buffer1) < frame_size1:
                    data_buffer1 += conn.recv(SIZE)
                frame_data1 = data_buffer1[:frame_size1]
                data_buffer1 = data_buffer1[frame_size1:]

                print("수신 프레임1 크기 : {} bytes".format(frame_size1))

                frame1 = pickle.loads(frame_data1)

                frame1 = cv2.imdecode(frame1, cv2.IMREAD_COLOR)
                print(frame1.shape)
                writer1.write(frame1)
                lock.release()
                time.sleep(0.15)
                
        elif mk == False:
            print("전송 : 프레임2")
            while len(data_buffer2) < data_size: #다 보냈는지 확인 -> 다 안보냈으면 전송
                data_buffer2 += conn.recv(SIZE) #보낼 data를 data_buffer에 넣고
                if len(data_buffer2) == 0: #보낼게 없으면
                    print("보낼 프레임2 없음")
                    c1 = True #다 전송했다고 알리기 위해 변수 c1을 True로 변경
                    lock.release()
                    break
            if c1 == False: #보낼게 있으면
                packed_data_size2 = data_buffer2[:data_size]
                data_buffer2 = data_buffer2[data_size:]

                frame_size2 = struct.unpack(">L", packed_data_size2)[0]

                while len(data_buffer2) < frame_size2:
                    data_buffer2 += conn.recv(SIZE)
                frame_data2 = data_buffer2[:frame_size2]
                data_buffer2 = data_buffer2[frame_size2:]

                print("수신 프레임2 크기 : {} bytes".format(frame_size2))

                frame2 = pickle.loads(frame_data2)

                frame2 = cv2.imdecode(frame2, cv2.IMREAD_COLOR)
                print(frame2.shape)
                writer2.write(frame2)
                lock.release()
                time.sleep(0.15)

        mk = np.invert(mk)
         
def main():
    global cl
    print("[STARTING] Server is starting")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen(10)
    print(f"[LISTENING] Server is listening on {IP}:{PORT}.")
    threads=[]
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        threads.append(thread)
        cl = len(threads)
        print(cl)
        if(cl == 2):
            break
            
    print(threads)
    threads[0].start()
    threads[1].start()
    threads[0].join()
    threads[1].join()
    conn.close()
    server.close()
    writer1.release()
    writer2.release()
    print("연결 종료")          

if __name__ == "__main__":
    lock = threading.Lock()
    main()
