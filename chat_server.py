import socket
from datetime import datetime
import zlib
from matplotlib.pyplot import text


MAX_BYTES = 1024
ADDRESS = '10.78.163.204'
PORT = 4545

def printwt(msg):
    ''' printwt message with current date and time '''

    current_date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'[{current_date_time}] {msg}')
    
def menu(sock ,Users_message):
    while True:
        data ,address = sock.recvfrom(MAX_BYTES)
        print(data)

        if (data == b'NEW'):
            sock.sendto('ALV'.encode('UTF-8').ljust(3, b'\0') ,address)
        elif (data == b'ALV'):
            sock.sendto('ALV'.encode('UTF-8').ljust(3, b'\0') ,address)
        else:
            print('Incorrect signal.')

        id = int.from_bytes(data[:16][0:4],byteorder='big')
        checksum = int.from_bytes(data[:16][4:8],byteorder='big')
        curr_package = int.from_bytes(data[:16][8:12],byteorder='big')
        tot_package = int.from_bytes(data[:16][12:16],byteorder='big')

        # print(f'id: {id}')
        # print(f'checksum: {checksum}')
        # print(f'curr_package: {curr_package}')
        # print(f'tot_package: {tot_package}')
            
        msg = data[16:]
        checksum_ser = checksum_calculator(msg)
        is_data_corrupted = checksum_ser != checksum

        if is_data_corrupted == False:
            text_list = msg.decode('UTF-8').split('  ')
            name = text_list[0]
            for user in Users_message.keys():
                if user != name:
                    sock.sendto('ACK'.encode('UTF-8').ljust(1024, b'\0') ,Users_message[user])
            printwt('ACK sent.')
        else:
            print('Data corrupted')

        if text_list[-1] == "new":
            Register(sock ,Users_message ,text_list ,address)
        if text_list[-1] == "/p":
            Public_chat(sock ,Users_message ,text_list)
        if text_list[-1] == "/s":
            Private_chat(sock ,Users_message ,text_list)
        if text_list[-1] == "/e":
            Exit(sock ,Users_message ,text_list)

def Register(sock ,Users_message ,text_list ,address):
    name = text_list[0]
    if name in Users_message.keys():
        sock.sendto('Error_UserExist'.encode('UTF-8') ,address)
        print(Users_message)
    else:
        Users_message[name] = address
        print(name + ' is enter the room')
        sock.sendto('OK'.encode('UTF-8') ,address)

def Public_chat(sock ,Users_message ,text_list):
    # print(text_list)
    name = text_list[0]
    #address = text_list[2]
    message = text_list[-2]
    data = ('[' + name + ']:' + message)
    for user in Users_message.keys():
        if user != name:
            sock.sendto(data.encode('UTF-8').ljust(1024, b'\0') ,Users_message[user])
    print('[' + str(datetime.now()) + ']' + '[' + name + ']:' + message)


def Private_chat(sock ,Users_message ,text_list):
    print(text_list)
    name = text_list[0]
    #address = text_list[2]
    message = text_list[2]
    Destination = text_list[3]
    data = ('[' + name + ']:' + message)
    for user in Users_message.keys():
        if user == Destination:
            sock.sendto(data.encode('UTF-8').ljust(1024, b'\0') ,Users_message[user])
            print('[' + str(datetime.now()) + ']' + '[' + name + ']' + ' to [' + Destination + ']: ' + message)


def Exit(sock ,Users_message ,text_list):
    name = text_list[0]
    address = text_list[1]
    print(address)
    data = 'BYE'
    for user in Users_message.keys():
        if name == user:
            sock.sendto(data.encode('UTF-8').ljust(1024, b'\0') ,Users_message[user])
            printwt(name + ' is quit the room\n')
            Users_message = removekey(Users_message, name)
    

def checksum_calculator(data):
    checksum = zlib.crc32(data)
    return checksum

def removekey(d, key):
    r = dict(d)
    del r[key]
    return r


def main():
    Users_message={}
    printwt('Creating socket...')
    sock = socket.socket(socket.AF_INET ,socket.SOCK_DGRAM)
    printwt('Socket created')
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024)
    printwt(f'Binding server to {ADDRESS}:{PORT}...')
    sock.bind((ADDRESS ,PORT))
    printwt(f'Server binded to {ADDRESS}:{PORT}')
    menu(sock ,Users_message)


if __name__ == "__main__":
    main()
