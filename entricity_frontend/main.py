from random import randint
import pygame, time
from typing import List,Dict
from threading import Lock

from pygame.key import get_pressed
from pygame.threads import Thread

from connections import Conn
import serialisation
from serialisation import deserialise_many

def smooth_position_update_x(entity, new_x):
    smoothing_factor = 0.1  # Adjust this value based on your needs
    entity.x += (new_x - entity.x) * smoothing_factor
def smooth_position_update_y(entity, new_y):
    smoothing_factor = 0.1  # Adjust this value based on your needs
    entity.y += (new_y - entity.y) * smoothing_factor

SCREEN_WIDTH, SCREEN_HEIGHT = (800,500)
ENTITY_BODY_SIZE = (20,20)
class Entity:
    def __init__(self, isid, x=0, y=0) -> None:
        self.isid = isid
        self.image = pygame.Surface(ENTITY_BODY_SIZE)
        self.rect = self.image.get_rect(topleft=(x,y))
        self.server_pos = pygame.Vector2()
        self.color = (255, 255, 255)
        self.state: int = 0
        self.direction: int = 0
    def draw(self, screen, *args, **kwargs):
        screen.blit(self.image, self.rect)
    def update(self, e):
        if e.x is not None:
            if abs(e.x - self.server_pos.x) > 100:
                print("x chage too high:", abs(e.x - self.server_pos.x))
            self.server_pos.x = e.x
            # smooth_position_update_x(self.server_pos, e.x)
        if e.y is not None:
            if abs(e.y - self.server_pos.y) > 100:
                print("y chage too high:", abs(e.y - self.server_pos.y))
            self.server_pos.y = e.y
            # smooth_position_update_y(self.server_pos, e.y)
        if e.state is not None:
            self.state = e.state
        if e.direction is not None:
            self.direction = e.direction

import json
SPEED = 200
class User:
    def __init__(self, name, id, isid) -> None:
        self.name = name
        self.id = id
        self.isid = isid
        self.entity: Entity = Entity(isid)
        self.accesstoken = "ZrMRX3Y360tEfqFfDCcvmAcnKUdfSRlPWEOB0FD0nzfUnb4Dii9XNL29R8qiC9pCVSslHk85AdkgqX1JNa5V0JvvR6z7CefF4IpVxahKrIF36UQboYFO0ACvnj87CjCgShnIcpnUcqLrNcnGVOoK0tJdZhOZPX7WqgErL52ZxCyYahQdnyoFaHZyAgdhNwRPBPjIRBhP2kgEYTJaUCETuc5TpmnkGkJjYGvYo80K5cLXyVMjI6pkXq1FDdI2uhTR"
    def move(self, dt):
        keys = pygame.key.get_pressed()
        dx = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
        dy = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
        if dx == 0 and dy == 0:
            return
        v = pygame.Vector2(dx, dy).normalize() * SPEED * dt
        self.entity.server_pos += v
        return self.entity.server_pos
        # print(self.entity.server_pos)
    def jsonify(self):
        # temp for id 6969 until acctual accounts are implemented
        data = {"name": self.name, "id": 6969, "accesstoken": self.accesstoken}
        jsonData = json.dumps(data)
        return data
        

game_entities: Dict[int,Entity] = {}

def update(dt, u, *args, **kwargs) -> None:
    u.move(dt)
    # print(dt)
    ...

def draw(screen, thlock,  *args, **kwargs) -> None:
    screen.fill((0,0,0))
    with thlock:
        for isid,e in game_entities.items():
            pygame.draw.rect(screen, e.color, pygame.Rect(int(e.server_pos.x),int(e.server_pos.y), 20,20))
    ...
def requestUserData(conn: Conn, isid: int) -> Entity:
    print(f"Requesting user data for: {isid=}")
    if isid < 0: raise ValueError("invalid in_server_id")
    data = {"type":"user_data_reques","message":{"in_server_id":isid}}
    conn.event_sock.send(conn.encode_message(json.dumps(data)))
    return Entity(isid, 0,0)
def get_game_data_thread_func(conn: Conn, thlock) -> None:
    while conn.conn_is_on:
        try:
            # probably delete deserialised entities length
            bytes_received, addr = conn.game_sock.recvfrom(1024)
            entitiesReceived, i = serialisation.unpack_uint32(bytes_received, 0)
            bytes_received = bytes_received[i:]
            if addr != conn.game_addr:
                raise Exception(f"Received data from an unknown address: {addr}")
            ets = deserialise_many(bytes_received)
            if len(ets) != entitiesReceived: raise ValueError(f"Did not received expexted length of entities: {entitiesReceived} got: {len(ets)}")
            with thlock:
                for e in ets:
                    if e.isid == conn.in_server_id: continue
                    if e.isid not in game_entities.keys():
                        new_entity = requestUserData(conn, e.isid)
                        game_entities[e.isid] = new_entity
                    else:
                        print("For entity", e.isid, e)
                        game_entities[e.isid].update(e)
        except Exception as e:
            print(e)
            conn.conn_is_on = False
    print("Exit get_game_data_thread_func thread")

if __name__ == "__main__":
    pygame.init()
    font = pygame.font.Font(None, 36)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Entricity")
    id = randint(0, 1023)
    u = User(f"Pablo{id}", id, -1)
    conn = Conn(u)
    game_entities[conn.in_server_id] = u.entity
    game_entities_lock = Lock()
    th = Thread(target=get_game_data_thread_func,args=(conn,game_entities_lock))
    th.daemon = True
    th.name = "get_data_thread"
    th.start()

    pt = time.time()
    try:
        while conn.conn_is_on:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    exit()
                
            t = time.time()
            dt, pt = t - pt, t

            update(dt, u)
            draw(screen=screen, thlock=game_entities_lock)
            text = f"len users: {len(game_entities)},{int(u.entity.server_pos.x)}:{int(u.entity.server_pos.y)}"
            text = f"len users: {len(game_entities)}|" + "|".join(
                [ f"{isid}@{int(e.server_pos.x)}:{int(e.server_pos.y)}" for
                    isid, e in game_entities.items() ]
            )
            text_surface = font.render(text, True, (255,0,0))
            screen.blit(text_surface, (0,0))
            pygame.display.flip()
            conn.send_game_data(int(u.entity.server_pos.x), int(u.entity.server_pos.y), 0, 69)
    except KeyboardInterrupt:
        conn.conn_is_on = False
        ...
    pygame.quit() 
    th.join()

