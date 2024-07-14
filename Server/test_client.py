import socket
import sys
import json
import struct
from threading import Thread


def encode_message(message):
    message_bytes = message.encode('utf-8')

    length = len(message_bytes)
    print(f"Length of message: {length}")
    # print(f"Message bytes: {message_bytes}")
    packed_message = struct.pack('>I', length) + message_bytes
    # print(f"Packed message: {packed_message}")
    input("<Enter> to send")
    return packed_message


def decode_message(sock: socket.socket):
    try:
        data = sock.recv(1024)
        length = struct.unpack('>I', data[:4])[0]
        bytes_got = len(data) - 4
        while bytes_got < length:
            additional_data = sock.recv(1024)
            data += additional_data
            bytes_got = len(data) - 4
        return str(data)
    except Exception as e:
        print(f"Error in receving data: {e}")
        return None
        

def receive_data(sock, on):
    while on[0]:
        try:
            message = decode_message(sock)
            if message is None:
                print("Server disconnected.")
                on[0] = False
            else:
                print("Received:", message)
        except Exception as e:
            print("Error:", e)
            on[0] = False

def main():
    streamSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        streamSock.connect(("0.0.0.0", 10101))
    except Exception as e:
        print(e, "Exiting")
        sys.exit()

    userData = {"id": 6969, "name": "Pablo"}
    bUserData = encode_message(json.dumps(userData))
    print("Sending user data:", bUserData)

    streamSock.send(bUserData)

    try:
        resp = decode_message(streamSock)
        if resp is not None:
            print("Response from server:", resp)
        else:
            print("No response or invalid response from server.")
            sys.exit()
    except Exception as e:
        print("Error receiving initial response:", e)
        sys.exit()

    on = [True]

    th = Thread(target=receive_data, args=(streamSock, on))
    th.daemon = True
    th.start()

    while on[0]:
        try:
            inp = input("Enter message: ")
            if inp.lower() == "exit":
                on[0] = False
                break
            jsonData = {"name": "Pablo", "message": inp}
            data = encode_message(json.dumps(jsonData))
            streamSock.send(data)
        except Exception as e:
            print("Error:", e)
            on[0] = False
            break

    th.join()
    streamSock.close()
    print("Exiting...")

if __name__ == "__main__":
    main()
