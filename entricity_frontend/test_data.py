import serialisation
import main, json
from typing import List,Dict
from threading import Thread

class GotData:
    def __init__(self,isid, x, y, s, d) -> None:
        self.isid = isid
        self.x:int|None= x
        self.y:int|None= y
        self.s:int|None= s
        self.d:int|None= d

if __name__ == "__main__":
    got_data = []
    game_entities: Dict[int,main.Entity] = {}
    u = main.User(f"test_user", 1123, -1)
    conn = main.Conn(u)
    def requestUserData(conn: main.Conn, isid: int) -> main.Entity:
        print(f"Requesting user data for: {isid=}")
        if isid < 0: raise ValueError("invalid in_server_id")
        data = {"type":"user_data_reques","message":{"in_server_id":isid}}
        conn.event_sock.send(conn.encode_message(json.dumps(data)))
        return main.Entity(isid, 0,0)
    def get_game_data_thread_func(conn: main.Conn) -> None:
        while conn.conn_is_on:
            try:
                bytes_received, addr = conn.game_sock.recvfrom(1024)
                if addr != conn.game_addr:
                    raise Exception(f"Received data from an unknown address: {addr}")
                for e in serialisation.deserialise_many(bytes_received):
                    if e.isid == conn.in_server_id: continue
                    if e.isid not in game_entities.keys():
                        new_entity = requestUserData(conn, e.isid)
                        game_entities[e.isid] = new_entity
                    else:
                        game_entities[e.isid].update(e)
                        ent = game_entities[e.isid]
                        gd = GotData(e.isid, None,None,None,None)
                        if e.x is not None:
                            if abs(e.x - ent.server_pos.x) > 100:
                                print("Too much")
                            else:
                                ent.server_pos.x = e.x
                            gd.x = e.x
                        if e.y is not None:
                            if abs(e.y - ent.server_pos.y) > 100:
                                print("Too much")
                            else:
                                ent.server_pos.y = e.y
                            gd.y = e.y
                        if e.state is not None:
                            ent.state = e.state
                            gd.s = e.state
                        if e.direction is not None:
                            ent.direction = e.direction
                            gd.d = e.direction
                        got_data.append(gd)
                    

            except Exception as e:
                print(e)
                conn.conn_is_on = False
        print("Exit get_game_data_thread_func thread")

    th = Thread(target=get_game_data_thread_func,args=(conn,))
    th.daemon = True
    th.name = "get_data_thread"
    th.start()
    try:
        while  conn.conn_is_on:
            conn.send_game_data(1,2, 0, 69)
    except KeyboardInterrupt:
        conn.conn_is_on = False
    print("end")
    print(got_data)
    th.join()
