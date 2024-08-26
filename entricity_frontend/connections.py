import socket, struct, json
from serialisation import serialise
# LOCAL_PUBLICK_ADDR = "0.0.0.0"
LOCAL_PUBLICK_ADDR = "192.168.0.5"

class Conn:
    def __init__(self, user) -> None:
        self.conn_is_on: bool = False
        self.user = user
        self.game_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.event_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.game_addr = (LOCAL_PUBLICK_ADDR, 12345)
        self.event_addr = (LOCAL_PUBLICK_ADDR, 10101)
        self.in_server_id: int = -1
        self.in_server_id_bytes: bytes
        self.connect_to_server()
        self.msgcount = 0

    def connect_to_server(self) -> None:
        try:
            self.event_sock.connect(self.event_addr)

            d = {"type":"request", "message":self.user.jsonify()}
            self.event_sock.send(self.encode_message(json.dumps(d)))

            response = self.receive_evet_message()
            if not response: raise Exception("No message received")

            js = json.loads(response)
            print(js)

            isid = js.get("in_server_id", None)
            if isid is None:
                raise ValueError("Missing in_server_id/invalid data received")

            self.in_server_id = isid
            self.in_server_id_bytes = struct.pack('>H', self.in_server_id)
            self.user.isid = isid
            self.user.entity.isid = isid
            self.conn_is_on = True
        except Exception as e:
            self.event_sock.close()
            raise e

    def receive_evet_message(self) -> bytes | None:
        try:
            # Receives first 1024 bytes of message
            data = self.event_sock.recv(1024)
            # If length of data is too small
            # (less than 0 or less then four [for first four bytes being length of acctual message])
            # raise Connection error
            if len(data) <= 0:
                raise ConnectionError("Server connection closed.")
            if len(data) <= 4:
                raise ConnectionError("Insufficent data.")
            # Get length of message [first four bytes]
            length = struct.unpack('>I', data[:4])[0]
            bytes_got = len(data) - 4

            # Keeps receving bytes unil length of 'data' is equal
            # to expected size
            while bytes_got < length:
                additional_data = self.event_sock.recv(1024)
                if len(data) <= 0:
                    raise ConnectionError("Server connection closed.")
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
        # Format {first four bytes are the size of 'message_bytes'}{message_bytes}
        packed_message = struct.pack('>I', length) + message_bytes
        return packed_message

    def send_game_data(self, x, y, s, d):
        angle = d%360
        data = bytearray()
        data.extend(self.in_server_id_bytes)
        data.extend(struct.pack('>I',self.msgcount))
        data.extend(serialise(isid=self.in_server_id, x=x, y=y, state=s, direction=angle))
        try:
            self.game_sock.sendto(data, self.game_addr)
            self.msgcount += 1
        except:
            print("Err")
