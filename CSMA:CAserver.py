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

IP = '172.20.10.13'
PORT = 8130
ADDR = (IP, PORT)
SIZE = 4096
a=0
n=4
cnt=0
#전송 전에 변수를 넣고 랜덤한 숫자를 뽑는다. if 30을 못넘으면, 다시 랜덤함수로 넣어라
#드론이 많을 때를 가정하기위해 하는 거임

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
writer1 = cv2.VideoWriter('./file1.mp4', fourcc, 24, (1080,1920))
writer2 = cv2.VideoWriter('./file2.mp4', fourcc, 24, (1080,1920))

def handle_client(conn, addr):
    data_buffer1 = b""
    data_buffer2 = b""
    data_size = struct.calcsize("L")
    flag = False
    
    while True:
        if a==1:
            while True:
                while len(data_buffer1) < data_size:
                    data_buffer1 += conn.recv(SIZE)
                    if len(data_buffer1) == 0:
                        flag = True
                        break
                if data_buffer1 == b'':
                    break

                packed_data_size1 = data_buffer1[:data_size]
                data_buffer1 = data_buffer1[data_size:]

                frame_size1 = struct.unpack(">L", packed_data_size1)[0]

                while len(data_buffer1) < frame_size1:
                    data_buffer1 += conn.recv(SIZE)
                frame_data1 = data_buffer1[:frame_size1]
                data_buffer1 = data_buffer1[frame_size1:]

                print("수신 프레임 크기 : {} bytes".format(frame_size1))

                frame1 = pickle.loads(frame_data1)

                frame1 = cv2.imdecode(frame1, cv2.IMREAD_COLOR)
                print(frame1.shape)
                writer1.write(frame1)
                if flag:
                    flag = False
                    break


        elif a==2:
            while True:
                while len(data_buffer2) < data_size:
                    data_buffer2 += conn.recv(SIZE)
                    if len(data_buffer2) == 0:
                        flag = True
                        break
                if data_buffer2 == b'':
                    break

                packed_data_size2 = data_buffer2[:data_size]
                data_buffer2 = data_buffer2[data_size:]

                frame_size2 = struct.unpack(">L", packed_data_size2)[0]

                while len(data_buffer2) < frame_size2:
                    data_buffer2 += conn.recv(SIZE)
                frame_data2 = data_buffer2[:frame_size2]
                data_buffer2 = data_buffer2[frame_size2:]

                print("수신 프레임 크기 : {} bytes".format(frame_size2))

                frame2 = pickle.loads(frame_data2)

                frame2 = cv2.imdecode(frame2, cv2.IMREAD_COLOR)
                print(frame2.shape)
                writer2.write(frame2)
                if flag:
                    flag = False
                    break
                    
        break

def random1(threads,x,y,conn):
    global n
    global a
    global cnt
    print(x,y)
    cnt+=1
    print(cl)
    if(x>y):
        #print('!')
        a=1
        xx=x-y
        sleep(y/100)
        threads[1].run()
        #print(xx)
        n=4
        y=random.randrange(0,15)
        if cnt<cl:
            random1(threads,xx,y,conn)
    elif(x<y):
        #print('?')
        a=2
        yy=y-x
        sleep(x/100)
        threads[0].run()
        #print(yy)
        x=random.randrange(0,15)
        n=4
        if cnt<cl:
            random1(threads,x,yy,conn)
#0~15
#충돌률 넣기        
    elif(x==y):
        n+=1
        x=random.randrange(0,2**n-1)
        y=random.randrange(0,2**n-1)
        if n == 10:
            x=random.randrange(0,1024)
            y=random.randrange(0,1024)
            random1(threads,x,y,conn)
        else:
            pass    
        return random1(threads,x,y,conn)    

def main():
    global n
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
    x=random.randrange(0,2**n-1)
    y=random.randrange(0,2**n-1)
    random1(threads,x,y,conn)
    conn.close()
    server.close()
    writer1.release()
    writer2.release()
    print("연결 종료")
                

if __name__ == "__main__":
    main()
