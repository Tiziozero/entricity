import socket, struct, json, select
from serialisation import serialise
# LOCAL_PUBLICK_ADDR = "0.0.0.0"
LOCAL_PUBLICK_ADDR = "192.168.0.5"

import time

last_send_time = time.time()
send_interval = 0.05  # 20 updates per second

def MaybeSendGameData(conn, x, y, s, d):
    global last_send_time
    current_time = time.time()
    if current_time - last_send_time > send_interval:
        conn.send_game_data(x, y, s, d)
        last_send_time = current_time

class Conn:
    def __init__(self) -> None:
        self.conn_is_on: bool = False
        self.game_addr = (LOCAL_PUBLICK_ADDR, 12345)
        self.event_addr = (LOCAL_PUBLICK_ADDR, 10101)
        self.msgcount = 0

        self.game_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.event_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Returns in server id
    def connectToServer(self, name:str, id:int) -> (int):
        try:
            self.event_sock.connect(self.event_addr)

            d = {"type":"connect", "message":{"name": name, "id": id, "accesstoken": "ZrMRX3Y360tEfqFfDCcvmAcnKUdfSRlPWEOB0FD0nzfUnb4Dii9XNL29R8qiC9pCVSslHk85AdkgqX1JNa5V0JvvR6z7CefF4IpVxahKrIF36UQboYFO0ACvnj87CjCgShnIcpnUcqLrNcnGVOoK0tJdZhOZPX7WqgErL52ZxCyYahQdnyoFaHZyAgdhNwRPBPjIRBhP2kgEYTJaUCETuc5TpmnkGkJjYGvYo80K5cLXyVMjI6pkXq1FDdI2uhTR"}}
            self.event_sock.send(self.encodeEventMessage(json.dumps(d)))

            response = self.receiveEventMessage()
            if not response: raise Exception("No message received")

            js = json.loads(response)
            print(js)

            isid = js.get("in_server_id", None)
            if isid is None:
                raise ValueError("Missing in_server_id/invalid data received")
            self.conn_is_on = True
            return isid
        except Exception as e:
            self.event_sock.close()
            self.conn_is_on = False
            raise e

    def receiveEventMessage(self) -> bytes:
        try:
            # Receives first 1024 bytes of message
            while self.conn_is_on:
                eventConnReadyForRead, _, _ = select.select([self.event_sock], [], [], 1)
                if eventConnReadyForRead:
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
                        eventConnReadyForRead, _, _ = select.select([self.event_sock], [], [], 1)
                        if eventConnReadyForRead:
                            additional_data = self.event_sock.recv(1024)
                            if len(data) <= 0:
                                raise ConnectionError("Server connection closed.")
                            data += additional_data
                            bytes_got = len(data) - 4
                    # returns only message_bytes
                    # {length of message_bytes}{message_bytes}
                    return data[4:]
            raise ValueError("event connection is closed.")
        except Exception as e:
            print(f"Error in receving data: {e}")
            self.conn_is_on = False
            raise e

    def encodeEventMessage(self, message:str) -> bytes:
        message_bytes = message.encode('utf-8')
        length = len(message_bytes)
        # Format {first four bytes are the size of 'message_bytes'}{message_bytes}
        packed_message = struct.pack('>I', length) + message_bytes
        return packed_message

    connMaxBufferSize: int = 64
    def sendGameData(self, isid:int, x:int|None=None, y:int|None=None, s:int|None=None, d:int|None=None):
        if x is None and y is None and s is None and d is None:
            return
        angle = d
        if d is not None:
            angle = d%360
        data = bytearray()
        gameData = serialise(isid=isid, x=x, y=y, state=s, direction=angle)
        data.extend(struct.pack('!H',isid))
        data.extend(struct.pack('>I',self.msgcount))
        data.extend(gameData)

        if len(data) > Conn.connMaxBufferSize:
            raise ValueError(f"Buffer too large. over {Conn.connMaxBufferSize} bytes.")
        try:
            self.game_sock.sendto(data, self.game_addr)
            self.msgcount += 1
        except Exception as e:
            raise e
    def receiveGameData(self) -> bytes:
        try:
            while self.conn_is_on:
                gameSockOnForReading, _, _ = select.select([self.game_sock], [], [], 1)
                if gameSockOnForReading:
                    b, addr = self.game_sock.recvfrom(1024)
                    if addr != self.game_addr:
                        raise ValueError("Address received from is not game server address")
                    if not b:
                        raise ValueError("No data retrived.")
                    return b
            raise ValueError("Game connection is closed.")
        except Exception as e:
            raise e
    def close(self) -> None:
        self.conn_is_on = False
        self.event_sock.close()
        self.game_sock.close()
