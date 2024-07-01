import socket, threading
from logger import log, warn

class ClientConnection:
    def __init__(self) -> None:
        self.event_conn: socket.socket
        self.game_conn:  socket.socket
        self.create_socket_connection()
        log("Created client connection object")


    def create_socket_connection(self) -> socket.socket:
        # self.event_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        warn("Connection not set. In development.")
        return socket.socket()
