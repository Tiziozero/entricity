from sys import exception
import pygame, json, struct, random, datetime
from time import sleep

from pygame.sprite import DirtySprite
from sprites import Entity
from typing import Dict, List
import entity_pb2 as pb
import socket
import threading
from constants import *

# const TEST_PORT_UDP = "localhost:3021"
# const TEST_PORT_TCP = "localhost:3020"
pygame.init()
pygame.font.init()
font_name = pygame.font.match_font('arial')  # You can also use a specific font file
font_size = 20
font = pygame.font.Font(font_name, font_size)


class TestSendEntity(Entity):
    def __init__(self, name:str="Unamed Entity", speed: int=200, groups: List[pygame.sprite.Group] = [], type: str = "any") -> None:
        super().__init__(name, speed, groups, type)
        self.color = (255,255,255)
        self.name_surf: pygame.Surface((0,0))

    def serialise(self) -> bytes:
        data = pb.Entity(
                x=int(self.pos.x),
                y=int(self.pos.y),
                animationIndex=int(self.sprite_sheet.animations.animation_index),
                direction=self.sprite_sheet.animations.facing,
                state=self.state )
        bytes_ = data.SerializeToString()
        return bytes_

    def move(self, dt: float) -> None:

        self.pos.x += self.velocity.x * dt
        self.pos.y += self.velocity.y * dt
        self.velocity.x = 0
        self.velocity.y = 0

    def update(self, dt: float, isUser=False) -> None:
        super().update()

        if isUser:
            self.__move(dt)
        else:
            v = pygame.Vector2(250 + random.randint(-500,0), 250 + random.randint(-500,0))
            self.velocity = v
        
        self.pos += self.velocity * dt
        self.velocity.x, self.velocity.y = 0, 0
        self.sprite_sheet.animations.animation_index += dt * self.sprite_sheet.animations.fps
    def __move(self, *args, **kwargs) -> None:
        k = pygame.key.get_pressed()
        # get velocity based on wasd
        x = int(k[pygame.K_d]) - int(k[pygame.K_a])
        y = int(k[pygame.K_s]) - int(k[pygame.K_w])
        f: pygame.Vector2
        if x == 0 and y == 0:

            f = pygame.Vector2()
        else:
            f = pygame.Vector2((x, y)).normalize()
        # set velocity
        s = self.speed
        if k[pygame.K_LSHIFT]: s = self.dash_speed
        self.velocity += f * s
        # print(dt, self.pos, self.velocity)
        # set FACING direction
        if self.velocity.y > 0: self.facing = DOWN
        elif self.velocity.y < 0: self.facing = UP
        if self.velocity.x > 0: self.facing = RIGHT
        elif self.velocity.x < 0: self.facing = LEFT
        
        # set state based on velocity from player
        if self.velocity.length() > 0:

            self.state = WALKING
        else:
            self.state = IDLE

        ...

class TestClient:
    def __init__(self, name:str="pablo", id:int=37) -> None:
        self.id = id
        self.name = name
        self.entity: TestSendEntity = TestSendEntity()
        self.entities: Dict[int, Entity] = {}
        self.mutex = threading.Lock()

        self.game_addr =  ("127.0.0.1", 3021)
        self.event_addr = ("127.0.0.1", 3020)
        self.game_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.event_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn_is_on = False


        self.in_server_id = 0
        self.in_server_id_bytes = b""

        try:
            self.event_sock.connect(self.event_addr)
        except Exception as e:
            print(f"Couldn't connect: {e}")
            raise e
        try:
            d = {"type":"request", "message":{"id": self.id, "name": self.name}}
            self.event_sock.send(
                    self.encode_message(json.dumps(d)))

            data = self.__receive_message()
            if data:
                d = json.loads(data.decode())
                # print(f"{self.id}:{self.name}data retreived: {d}")
                id = d.get("in_server_id", None)
                if id:
                    self.in_server_id = int(id)
                    self.in_server_id_bytes = struct.pack('>H', self.in_server_id)
                    # print(f"In server id = {self.in_server_id}, {self.in_server_id_bytes}")
                else:
                    # print(f"{self.id}:{self.name} id: {id}. invalid id")
                    raise Exception(f"{self.id}:{self.name}Server data is invalid/id is invalid")
            self.conn_is_on = True
        except Exception as e:
            print(f"{self.id}:{self.name}Exception in creating user conn: {e}")
            raise e
        print("Created user with:", self.id, self.in_server_id)

    def quit(self):
        self.conn_is_on = False
        try:
            self.event_sock.send(self.encode_message(json.dumps({"type":"event", "message":"quit"})))
            print("sent quit message")
        except Exception as e:
            print(e)


    def update(self, dt:float, isUser=False) -> None:
        self.mutex.acquire()
        self.entity.update(dt, isUser)
        self.mutex.release()
            
        ...

    def send_game_data(self) -> None:
        data = self.entity.serialise()
        data = self.in_server_id_bytes + data
        self.game_sock.sendto(
            data, self.game_addr)
    def get_game_data(self) -> None:
        try:
            # print("Before received from game sock")
            b, addr = self.game_sock.recvfrom(1024)
            # print("Received from game sock")
            if addr != self.game_addr:
                raise Exception(f"{self.id}:{self.name} Address does not match server address: {addr}, {self.game_addr}")
            
            if len(b) == 0:
                raise Exception("data too short: 0")
            # Parse the received data as Message
            message = pb.Message()
            try:
                message.ParseFromString(b)
            except:
                raise Exception("Protoduf faild to deserialize game data")

            # Print entities
            for e in message.entities:
                try:
                    en = self.entities.get(e.inServerId, None)
                    if en == self:
                        print("found self")
                except:
                    raise Exception(f"Filed to get entity: in server id: {e.inServerId}")

                if not en:
                    en = Entity()
                    c = random.choice([
                        (255,0,0),
                        (0,255,0),
                        (0,0,255),
                        (0,125,125),
                        (0,255,125),
                        (0,125,255),
                        (125,125,0),
                        (255,125,0),
                        (125,255,0)
                        ])
                    en.name_surf = font.render(f"{e.inServerId}", True, c)
                    en.image = pygame.Surface((20,20))
                    en.color=c
                    en.image.fill(en.color)
                    en.rect = en.image.get_rect()
                    en.in_server_id = e.inServerId
                en.pos.x = e.x
                en.pos.y = e.y
                en.state = e.state
                en.sprite_sheet.animations.facing = e.direction
                en.sprite_sheet.animations.animation_index = e.animationIndex
                self.entities[en.in_server_id] = en
            # Print events
            # for event in message.events:
            #     print(f"{self.id}:{self.name} From server event:", str(event).split('\n'))

        except Exception as e:
            print(f"{self.id}:{self.name} Error in receiving from game conn: {e}\n\t")

    def get_events_loop(self):
        while self.conn_is_on:
            try:
                data = self.__receive_message()
                if not data or len(data) == 0:
                    print("Received None, quiting connection")
                    self.quit()
                print(data.decode())
                jsonData = json.loads(data)
                type = jsonData.get("type", None)
                if type == None or type == "error":
                    print(f"Error in get_events_loop: {type}")
                    raise Exception(f"Missing or invalid type: {type}")
            except Exception as e:
                print(f"{e} in get events loop")
                self.quit()
                
    def getGameDataThreadFunc(self):
        t = threading.Thread(target=self.get_events_loop)
        t.daemon = True
        t.name = "thisUser event loop"
        t.start()
        while self.conn_is_on:
            self.get_game_data()
        print("Ended game data receiver")
        t.join()

    # Method to receive messages
    def __receive_message(self) -> bytes | None:
        try:
            data = self.event_sock.recv(1024)
            if len(data) <= 0 and len(data) <=4:
                raise ConnectionError("Server connection closed.")
            # Get length of message [first four bytes]
            length = struct.unpack('>I', data[:4])[0]
            bytes_got = len(data) - 4

            while bytes_got < length:
                additional_data = self.event_sock.recv(1024)
                data += additional_data
                bytes_got = len(data) - 4
            return data[4:]
        except Exception as e:
            print(f"Error in receving data: {e}")
            self.conn_is_on = False
            return None


    def encode_message(self, message:str) -> bytes:
        message_bytes = message.encode('utf-8')
        length = len(message_bytes)

        packed_message = struct.pack('>I', length) + message_bytes
        return packed_message


if __name__ == "__main__":
    thisUser = TestClient("Pablo", random.randint(0, 6969))
    thisUserThread = threading.Thread(target=thisUser.getGameDataThreadFunc, args=[])
    thisUserThread.name = "thisUserThread"
    thisUserThread.daemon = True
    thisUserThread.start()

    s = pygame.display.set_mode((1000, 600))
    font_name = pygame.font.match_font('arial')  # You can also use a specific font file
    font_size = 20
    font = pygame.font.Font(font_name, font_size)

    clock = pygame.time.Clock()


    def DisplayUsers(user:TestClient, screen):
        surf = pygame.display.get_surface()
        data = user.entities.items()
        i = 0
        for isid, e in data:
            e.rect.centerx = int(e.pos.x)
            e.rect.centery = int(e.pos.y)
            print(e.rect.center)
            screen.blit(e.image, e.rect)
            i += 1
        return i

    while thisUser.conn_is_on:
        try:
            thisUser.send_game_data()
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    thisUser.quit()


            dt = clock.tick(60) / 1000  # Convert milliseconds to seconds
            thisUser.update(dt, isUser=True)


            s.fill((0,0,0))
            # text = f"FPS: {clock.get_fps():.2f} DT: {dt}"
            # fpsSurface = font.render(text, True, (255,255,255))
            # s.blit(fpsSurface, (0,0))
            users = DisplayUsers(thisUser, s)
            text = f"Pos: {thisUser.entity.pos.x:.2f}:{thisUser.entity.pos.y:.2f}; State: {thisUser.entity.state}; Dirrection: {thisUser.entity.direction}: length of entities: {users}"
            fpsSurface = font.render(text, True, (255,255,255))
            s.blit(fpsSurface, (0,30))
            # print(f"users length: {len(users)}")
            pygame.display.update()
        except KeyboardInterrupt:
            thisUser.quit()
    print("End of loop")

    # thisUserThread.join()
    print("End of main")
