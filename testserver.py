import socket

# Addresses and ports
GAME_PORT = 3021
EVENT_PORT = 3020
LOCALHOST = "127.0.0.1"

# Setup UDP socket for game data
game_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
game_sock.bind((LOCALHOST, GAME_PORT))

# Setup TCP socket for events
event_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
event_sock.bind((LOCALHOST, EVENT_PORT))
event_sock.listen(1)

print("Server is running...")

# Handle connections and data
try:
    while True:
        # UDP for game data
        try:
            data, addr = game_sock.recvfrom(1024)
            print(f"Received game data: {data.decode()} from {addr}")
        except socket.error as e:
            print(f"UDP socket error: {e}")

        # TCP for event data
        try:
            conn, addr = event_sock.accept()
            print(f"Event connection from {addr}")
            event_data = conn.recv(1024)
            print(f"Received event data: {event_data.decode()}")
            conn.close()
        except socket.error as e:
            print(f"TCP socket error: {e}")
except KeyboardInterrupt:
    print("Server shutting down.")
finally:
    game_sock.close()
    event_sock.close()

