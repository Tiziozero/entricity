import socket, json
import struct
from threading import Thread
from typing import Any
from logger import log, err
import serialisation

import entity_pb2 as pb

class Connections:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance == None:
            cls._instance = super(Connections, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self) -> None:
        if hasattr(self, 'initialized') and self.initialized:
            return

        self.stream_sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.game_sock:  socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.game_conn_server_addr = ("127.0.0.1", 12345)
        self.stream_conn_addr = ("127.0.0.1", 10101)
        self.game_conn_server_addr = ("192.168.0.5", 12345)
        self.stream_conn_addr = ("192.168.0.5", 10101)
        self.conn_is_on: bool = False
        self.listener_thread: Thread = Thread()
        self.in_server_id: int
        self.in_server_id_bytes: bytes
        # Connections to server and socket initialisations
        try:
            d = {"type":"request", "message":{"id": 6969, "name":"Pablo"}}
            self.stream_sock.connect(self.stream_conn_addr)
            self.stream_sock.send(
                    self.encode_message(
                        json.dumps(d)
                        )
                    )
            data = self.__receive_message()
            if data:
                d = json.loads(data.decode())
                id = d.get("in_server_id", None)
                log(f"data retreived: {d}")
                if id:
                    self.in_server_id = int(id)
                    self.in_server_id_bytes = struct.pack('>H', self.in_server_id)
                else:
                    err(f"id: {id}")
                    raise Exception("Server data is invalid/id is invalid")

            self.conn_is_on = True
        except Exception as e:
            err(f"Exception in creating user conn: {e}")
            raise e

        self.listen_to_server_messages()
        log("Socket Connection created successfully")
        self.initialized = True

    # Sends data via UDP !!!TO IMPLEMENT format {in_server_id}{message_bytes}
    def send_game_conn(self, bytes: bytes) -> None:
        try:
            bytes = self.in_server_id_bytes+bytes
            # print(self.in_server_id_bytes, self.in_server_id, bytes)
            self.game_sock.sendto(bytes, self.game_conn_server_addr)
        except Exception as e:
            err(f"Error in sending to game_sock: {e}")

    # Sends data via TCP connection
    def send_stream_message(self, data: str) -> None:
        try:
            # Encodes message {length of message_bytes}{message_bytes}
            b = self.encode_message(data)
            print("sending: " + b[4:].decode())
            # Sends message
            self.stream_sock.send(b)
        except Exception as e:
            err(f"Error in sending message to server stream: {e}")

    # Method to receive messages
    def __receive_message(self) -> bytes | None:
        try:
            # Receives first 1024 bytes of message
            data = self.stream_sock.recv(1024)
            # If length of data is too small
            # (less than 0 or less then four [for first four bytes being length of acctual message])
            # raise Connection error
            if len(data) <= 0 and len(data) <=4:
                raise ConnectionError("Server connection closed.")
            # Get length of message [first four bytes]
            length = struct.unpack('>I', data[:4])[0]
            bytes_got = len(data) - 4

            # Keeps receving bytes unil length of 'data' is equal
            # to expected size
            while bytes_got < length:
                additional_data = self.stream_sock.recv(1024)
                data += additional_data
                bytes_got = len(data) - 4
            # returns only message_bytes
            # {length of message_bytes}{message_bytes}
            return data[4:]
        except Exception as e:
            print(f"Error in receving data: {e}")
            self.conn_is_on = False
            return None


    def encode_message(self, message:str) -> bytes:
        message_bytes = message.encode('utf-8')
        length = len(message_bytes)

        # print(f"Length of message: {length}")
        # Format {first four bytes are the size of 'message_bytes'}{message_bytes}
        packed_message = struct.pack('>I', length) + message_bytes
        return packed_message

    def listen_to_server_messages(self) -> None:
        def __listener(self):
            try:
                while self.conn_is_on:
                    message = self.__receive_message()
                    if message == None or len(message) == 0:
                        raise ConnectionError("Connection to server closed.")
                    print(f"received: \"{message.decode()}\" from server")
            except Exception as e:
                err(f"Got Error from connections listener: {e}")
                self.conn_is_on = False

        self.listener_thread = Thread(target=__listener, args=(self,))
        self.listener_thread.daemon = True
        self.listener_thread.name = "Listener Thread"
        self.listener_thread.start()
                
    def send_game_data(self, ent: Any) -> None:
        """
            class EntityStates(Enum):
                IDLE        = 1
                WALKING     = 2
                ATTACKING   = 3

            class EntityDirections(Enum):
                LEFT        = 1
                RIGHT       = 2
                UP          = 3
                DOWN        = 4
        """
        pos = ent.pos
        animation_index = ent.frame_index
        facing = ent.facing
        state = ent.state
        serialisation.serialise()
        bytes_ = data.SerializeToString()
        self.send_game_conn(bytes_)

    def receive_game_data(self):
        try:
            print("getting message")
            b, addr = self.game_sock.recvfrom(1024)
            if addr != self.game_conn_server_addr:
                raise Exception(f"Address does not match server address: {addr}, {self.game_conn_server_addr}")
            
            # Parse the received data as Message
            message = pb.Message()
            message.ParseFromString(b)

            # Print entities
            for e in message.entities:
                print("From server entity:", str(e).split('\n'))

            # Print events
            for event in message.events:
                print("From server event:", str(event).split('\n'))
            return message.entities, message.events


        except Exception as e:
            err(f"Error in receiving from game conn: {e}")
            return [],[]
        ...


    def __del__(self) -> None:
        self.conn_is_on = False
        try:
            self.stream_sock.close()
        finally:
            log("Closed Connection")


if __name__=="__main__":
    c = Connections()
    while True:
        try:
            c.send_game_conn(b"Hewwo Uwu")
        except:
            break
