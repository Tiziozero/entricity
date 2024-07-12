import socket
import struct
import time
import string
from  random import choice, randint
from threading import Thread

# Define the server address and port
server_address = ('127.0.0.1', 12345)
message = 10  # uint16 value to send


def getRadnStr(n) -> str:
    arr = string.ascii_letters
    arr += string.digits
    o = ""
    for i in range(n):
        o += choice(arr) + str(i)
    return o

def f():
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    id = getRadnStr(randint(3, 9))
    try:
        for i in range(150):
            # Pack the uint16 value into a byte array
            # message = "".join([str(j) for j in range(i)])
            message = "USR<" + f"{str(id): >10}" + ">  " + getRadnStr( 30+i)
            
            encoded_message = message.encode()
            data = struct.pack('!H', len(encoded_message) + 2)  # '!H' denotes network order (big-endian) unsigned short
            data += encoded_message
            # Send the data to the server
            sock.sendto(data, server_address)
            print(f"Thread {id} sent {message}")
            # Optional: wait for a short time between sends
            time.sleep(randint(0, 1) * 0.001)

    finally:
        print('Closing socket')
        sock.close()
ths = []
for _ in range(100):
    th = Thread(target=f, args=[])
    th.daemon = True
    th.start()
    ths.append(th)
for t in ths:
    t.join()

