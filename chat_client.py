import socket
import sys
from multiprocessing import Process
import os
import zlib
import struct
import random
from datetime import datetime


MAX_BYTES = 1024
ADDRESS = '10.78.163.204'
# ADDRESS = '10.77.115.174'
PORT = 4545

def printwt(msg):
    ''' printwt message with current date and time '''

    current_date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'[{current_date_time}] {msg}')

# Send info to server
def Person_Message(sock ,choice):
    name = input('Please input name: ')
    text = name + '  ' + str(choice)
    data = text.encode('UTF-8')

    curr_package = int(0).to_bytes(4, byteorder='big')
    tot_package = int(1).to_bytes(4, byteorder='big')
    id = random.randbytes(4)
    checksum = checksum_calculator(data).to_bytes(4, byteorder='big')

    udp_header = id + checksum + curr_package + tot_package
    msg = udp_header + data
    sock.sendto(msg ,(ADDRESS ,PORT))

    data ,address= sock.recvfrom(MAX_BYTES)
    return data.decode('UTF-8') ,name ,address


# Message to public channel
def Chat_Message(sock ,name ,address):
    print('Please enter the chat content:\n\n(input \033[1;44mExit\033[0m to quit the room,\n'
          'input \033[1;44ms/name/message\033[0m for Private chat)\t\t\tHistory:')
    p = Process(target = rcvmsg ,args = (sock ,name ,address))
    p.start()
    sendmsg(sock ,name ,address)


def sendmsg(sock ,name ,address):
    while True:
        message = input()
        Words = message.split('/')
        curr_package = int(0).to_bytes(4, byteorder='big')
        tot_package = int(1).to_bytes(4, byteorder='big')
        id = random.randbytes(4)
        if Words[0] == 's':
            Destination = Words[1]
            true_message = Words[2]
            text = f'{name}  {str(address)}  {true_message}  {Destination}  /s'
            # '4' + '  ' + name + '  ' + str(address) + '  ' + true_message + '  ' + Destination
            data = text.encode('UTF-8')
            checksum = checksum_calculator(data).to_bytes(4, byteorder='big')
            udp_header = id + checksum + curr_package + tot_package

            msg = udp_header + data
            sock.sendto(msg ,(ADDRESS , PORT))
            print('Sent!')
        elif message == 'Exit':
            text = name + '  ' + str(address) + '  ' + name + ' has left the room' + '  ' + '/p'
            data = text.encode('UTF-8')

            checksum = checksum_calculator(data).to_bytes(4, byteorder='big')
            udp_header = id + checksum + curr_package + tot_package
            msg = udp_header + data
            sock.sendto(msg ,(ADDRESS ,PORT))

            text_2 = name + '  ' + str(address) + '  ' + '/e'
            data_2 = text_2.encode('UTF-8')
            id_2 = random.randbytes(4)
            checksum_2 = checksum_calculator(data_2).to_bytes(4, byteorder='big')
            udp_header_2 = id_2 + checksum_2 + curr_package + tot_package
            msg_2 = udp_header_2 + data_2
            sock.sendto(msg_2 ,(ADDRESS ,PORT))

            # Send BYE 3 bytes to the server
            sock.sendto('BYE'.encode('UTF-8') ,(ADDRESS ,PORT))

            sys.exit('You have exited the chat room\n')
        else:
            text = name + '  ' + str(address) + '  ' + message + '  ' + '/p'
            # text = message
            
            data = text.encode('UTF-8')
            checksum = checksum_calculator(data).to_bytes(4, byteorder='big')

            udp_header = id + checksum + curr_package + tot_package
            msg = udp_header + data
            sock.sendto(msg ,(ADDRESS ,PORT))

            # Send ALV 3 bytes to the server    
            sock.sendto('ALV'.encode('UTF-8') ,(ADDRESS ,PORT))


def read_bytes(sock, num_bytes: int):
    data = bytes()
    waiting_for_bytes = num_bytes
    while waiting_for_bytes >0:
        msg, addr = sock.recvfrom(waiting_for_bytes)

        received_bytes: bytes = msg
        data += received_bytes
        waiting_for_bytes -= len(received_bytes)
        # print(waiting_for_bytes)
        # print(data)

    return data, addr

# Receive message
def rcvmsg(sock ,name ,address):
    while True:
        full_packet ,address= read_bytes(sock,1024)
        data = full_packet.decode('UTF-8')

        print(data)
        if data == 'BYE':
            os._exit(0)
        else:
            print('\t\t\t\t\t\t' + data)

def checksum_calculator(data):
    checksum = zlib.crc32(data)
    return checksum
    
def main():
    printwt('Creating UDP/IPv4 socket ...')
    sock = socket.socket(socket.AF_INET ,socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024)
    printwt(f"Send to server {ADDRESS}")
    printwt(f"Socket created")

    printwt("Send NEW signal to the server")
    sock.sendto('NEW'.encode('UTF-8').ljust(3, b'\0') ,(ADDRESS ,PORT))
    full_packet ,address= read_bytes(sock,3)
    data = full_packet.decode('UTF-8')

    ## Shd receive ALV from server
    printwt(data)

    printwt("Send ALV signal to the server")
    sock.sendto('ALV'.encode('UTF-8').ljust(3, b'\0') ,(ADDRESS ,PORT))
    full_packet ,address= read_bytes(sock,3)
    data = full_packet.decode('UTF-8')

    while True:
        signal ,name ,address = Person_Message(sock ,'new')
        print(address)
        if signal == 'OK':
            print('\t\t\t\tYou have successfully entered the room\t\t')

            text = name + '  ' + str(address) + '  ' + name + ' has entered the room' + '  ' + '/p'
            data = text.encode('UTF-8')

            curr_package = int(0).to_bytes(4, byteorder='big')
            tot_package = int(1).to_bytes(4, byteorder='big')
            id = random.randbytes(4)
            checksum = checksum_calculator(data).to_bytes(4, byteorder='big')

            udp_header = id + checksum + curr_package + tot_package
            msg = udp_header + data
            sock.sendto(msg ,(ADDRESS ,PORT))

            # send NEW 3 bytes to the server
            sock.sendto('NEW'.encode('UTF-8') ,(ADDRESS ,PORT))
            break
        elif signal == 'Error_UserExist':
            print('User already exists!')
    Chat_Message(sock ,name ,address)


if __name__ == "__main__":
    main()
