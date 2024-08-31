import socket, json
import struct
from threading import Thread
from typing import Any
from logger import log, err
import serialisation


class Connections:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance == None:
            cls._instance = super(Connections, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self) -> None:
        if hasattr(self, 'initialized') and self.initialized:
            return

        self.event_conn: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.game_conn:  socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.game_conn_server_addr = ("127.0.0.1", 12345)
        self.stream_conn_addr = ("127.0.0.1", 10101)
        # self.game_conn_server_addr = ("192.168.0.5", 12345)
        # self.stream_conn_addr = ("192.168.0.5", 10101)

        self.conn_is_on: bool = False
        self.listener_thread: Thread = Thread()
        self.in_server_id: int
        self.in_server_id_bytes: bytes

        # Connections to server and socket initialisations
        try:
            d = {"type":"request", "message":{"id": 6969, "name":"Pablo"}}
            self.event_conn.connect(self.stream_conn_addr)
            self.event_conn.send(
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
        # Initialise UDP addr for server
        self.send_game_conn(b'\x00'+ self.in_server_id_bytes)
        log("Socket Connection created successfully")
        self.initialized = True

    # Sends data via UDP
    def send_game_conn(self, bytes: bytes) -> None:
        try:
            bytes = self.in_server_id_bytes+bytes
            self.game_conn.sendto(bytes, self.game_conn_server_addr)
        except Exception as e:
            self.conn_is_on = False
            err(f"Error in sending to game_conn: {e}")

    # Sends data via TCP connection
    def send_event_message(self, data: str) -> None:
        try:
            b = self.encode_message(data)
            self.event_conn.send(b)
        except Exception as e:
            err(f"Error in sending message to server stream: {e}")

    # Method to receive messages
    def __receive_message(self) -> bytes | None:
        try:
            # Receives first 1024 bytes of message
            data = self.event_conn.recv(1024)
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
                additional_data = self.event_conn.recv(1024)
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
            log("Listening to sermer events")
            try:
                while self.conn_is_on:
                    message = self.__receive_message()
                    if message == None or len(message) <= 0:
                        self.quit()
                    print("".join(["-" for _ in range(120)]))
                    print(f"received: \"{message.decode()}\" from server")
                    print("".join(["-" for _ in range(120)]))
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
        e = serialisation.EntitySerialisationData()
        e.setPosX(ent.state.pos.x)
        e.setPosY(ent.state.pos.y)
        e.setState(ent.state.state)
        e.setDirection(ent.state.direction)
        data = bytearray()
        data.append(0x00)
        data.extend(self.in_server_id_bytes)
        data.extend(serialisation.serialise(e))
        self.send_game_conn(data)

        # input game_is_on in arr_with_bool
    def receive_game_data(self) -> bytes:
        try:
            # print("getting message")
            b, addr = self.game_conn.recvfrom(1024)
            if addr != self.game_conn_server_addr:
                raise Exception(f"Address does not match server address: {addr}, {self.game_conn_server_addr}")
            return b
        except Exception as e:
            err(f"Error in receiving from game conn: {e}")
            return b''

    def quit(self):
        self.conn_is_on = False
        try:
            self.event_conn.send(self.encode_message(json.dumps({"type":"event", "message":"quit"})))
            print("sent quit message")
        except Exception as e:
            print(e)
        finally:
            self.event_conn.close()

    def __del__(self) -> None:
        self.conn_is_on = False
        try:
            self.quit()
        finally:
            log("Closed Connection")


if __name__=="__main__":
    c = Connections()
    while True:
        try:
            c.send_game_conn(b"Hewwo Uwu")
        except:
            break
