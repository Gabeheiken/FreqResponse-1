import csv
import os
import socket  # Import libraries
import time
from time import sleep
from timer import timer

# import GS_computer as catch
import easygui


# Gabe's method for sending archive file to grid simulator when new RTAC recording has begun.
# This code utilizes the unraid server that is connected to both the grid sim and the RTAC computer,
# so there is no need to ping back and forth when a file has begun.
# This code builds on the Umar_GS code

def conn():
    global s
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1000)
    s.connect(('192.168.0.149', 5025))  # NHR 9410 IP address
    output = 'SYST:RWL\n'  # Lock the touch panel screen (Safety purpose)
    s.send(output.encode('utf-8'))  # For each SCPI command, it MUST encoded into utf-8.
    return s


def clos(s):  # This function is meant to close the connection
    output5 = 'SYST:LOC\n'  # Unlock the touch panel screen
    s.send(output5.encode('utf-8'))
    s.close()  # Close the connection



def Gs(file):
    global length1
    global j
    global path
    path = "Z:/RTAC_Recordings2"
    arr = []
    curr = time.time()
    t = timer()
    av = []



    with open(f"{file}") as csv_file:
        print(file)
        csv_reader = csv.DictReader(csv_file, delimiter=',')
        i = 1
        for rows in csv_reader:
            y = rows['STATION_1:Freq']
            y = float(y) + 0.01203651
            y = round(y, 6)
            arr.append(y)

    conn()
    # s.send('FREQ 60.00 \n'.encode('utf-8'))
    s.send('MACR :LEAR 1 \n'.encode('utf-8'))
    # print("sent1")
    s.send('MACR:OPER:SYNC:INST1 SYNC \n'.encode('utf-8'))
    # print("sent2")
    s.send('MACR:LEAR 0 \n'.encode('utf-8'))
    # print("sent4")
    s.send('MACR:RUN \n'.encode('utf-8'))
    # print("sent5")
    output2 = 'FREQ '
    m = 1

    # If file is less than 18000 lines, fills end with 60s
    for i in range(18000):
        if i > len(arr):
            arr.append(60)

    while time.time() < (curr + 8): # 11.5   There is a delay before the next RTAC file begins recording
        pass

    for i in arr:
        start_time = time.time()*1000
        var = output2 + str(i) + '\n'
        s.send(var.encode('utf-8'))
        print('frequency value: ', i, ' in line ', m, '\n')
        m = m + 1

        while (time.time()*1000) < (start_time + 33): # 33 31.22
            pass


        tot = time.time() - curr
        print('Total time: ', round(tot,3))
        if time.time() > (curr + 606): #609.5
            lis2 = os.listdir(path)
            length2 = len(lis2)
            print(length1)
            print(length2)
            if length2 > length1:
                length1 = length2
                break
            print('Here')

        tot1 = time.time() - start_time/1000
        freq = 1 / tot1
        av.append(freq)
        print('Send freq: ', round(freq, 3))
        print('Avg:', sum(av) / len(av))
        if freq < 25:
            print('SEND FREQUENCY TOO SLOW! RESTART TEST')
        if m == 17999:
            while True:
                lis2 = os.listdir(path)
                length2 = len(lis2)
                if length2 > length1:
                    length1 = length2
                    break

    clos(s)


filePath = easygui.fileopenbox("Select archive file to send: ", "", filetypes="*.csv", multiple=True)
print(filePath)
path = "Z:/RTAC_Recordings2"
lis = os.listdir(path)
length = len(lis)

# ans = input('Would you like to run another test? y/n \n')
# if ans == 'y':
#     filePath2 = easygui.fileopenbox("Select archive file to send: ", "", filetypes="*.csv", multiple=True)
#     filePath.append(filePath2)

print('Waiting for new RTAC recording file...')


while True:
    lis1 = os.listdir(path)
    length1 = len(lis1)
    if length < length1:
        start = time.time()
        for j in range(len(filePath)):
            Gs(filePath[j])

        break




