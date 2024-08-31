from random import randint
import pygame, threading, time
from typing import Dict, List

from connections import Conn
import serialisation

class EntityState:
    def __init__(self, x=0, y=0, s=0, d=0) -> None:
        self.x:int = x
        self.y:int = y
        self.state:int = s
        self.direction:int = d
    def copy(self):
        return EntityState(self.x, self.y, self.state, self.direction)
        
class Entity:
    def __init__(self, isid:int) -> None:
        self.isid:int = isid
        self.PS: EntityState = EntityState()
        self.CS: EntityState = EntityState()
    def update(self, e: serialisation.retVal) -> None:
        if e.x is not None: self.CS.x = e.x
        if e.y is not None: self.CS.y = e.y
        if e.state is not None: self.CS.state = e.state
        if e.direction is not None: self.CS.direction = e.direction

class Game:
    def __init__(self, name:str=f"pablo{randint(0,1234)}",id:int=6969) -> None:
        self.name = name
        self.id = id
        self.conn: Conn = Conn()
        self.isid: int
        self.gameEntities:Dict[int,Entity]= {}
        try:
            self.isid = self.conn.connectToServer(self.name, self.id)
        except Exception as e:
            print(e)
            exit(-1)
        self.gameEntity = Entity(self.isid)
        self.gameEntities[self.isid] = self.gameEntity
        self.gameIsOn:bool = True
    def getGameData(self) -> None:
        try:
            b = self.conn.receiveGameData()
            _, offset = serialisation.unpack_uint32(b)
            entities = serialisation.deserialise_many(b[offset:])
            for e in entities:
                if e.isid == self.isid: continue
                ent = self.gameEntities.get(e.isid, None)
                if ent == None:
                    print("New Entity")
                    ent = self.getEntityData(e.isid)
                    self.gameEntities[e.isid] = ent
                ent.update(e)
        except Exception as e:
            print(e)
    def sendGameData(self) -> None:
        try:
            e = self.gameEntity
            x = None
            y = None
            s = None
            d = None
            if e.CS.x != e.PS.x: x = e.CS.x
            if e.CS.y != e.PS.y: y = e.CS.y
            if e.CS.state != e.PS.state: s = e.CS.state
            if e.CS.direction != e.PS.direction: d = e.CS.direction

            self.conn.sendGameData(self.isid,
                                   int(x) if x is not None else None,
                                   int(y) if y  is not None else None,
                                   int(s) if s is not None else None,
                                   int(d) if d is not None else None,
                                   )
            self.gameEntity.PS = self.gameEntity.CS
            self.gameEntity.CS = self.gameEntity.CS.copy()
        except Exception as e:
            raise e
    # TODO: implement this crap
    def getEntityData(self, isid):
        return Entity(isid)
    def close(self) -> None:
        self.gameIsOn = False
        self.conn.close()
        print("Game closed")

def handelPlayerMovement(p: Entity, dt):
    keys = pygame.key.get_pressed()
    xm = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
    ym = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
    speed = 200
    if keys[pygame.K_RCTRL]: speed *= 3
    p.CS.x += xm*speed * dt
    p.CS.y += ym*speed * dt

pygame.font.init()
GLOBALDRAWFONT = pygame.font.SysFont('Arial', 25)
def drawGameEntities(screen: pygame.Surface, es: Dict[int,Entity]):
    for i,(_,e) in enumerate(sorted(es.items())):
        text = f"{e.isid: >3}@[{int(e.CS.x): >5}]:[{int(e.CS.y): >5}]s:{e.CS.state: >3};d:{e.CS.direction: >5}"
        s = GLOBALDRAWFONT.render(text, True, (255,255,255))
        screen.blit(s, (0,i*30))
        pygame.draw.circle(screen, (255,0,0), (e.CS.x, e.CS.y), 10,0)

def GameGetGameData(g: Game):
    while g.gameIsOn:
        try:
            g.getGameData()
        except Exception as e:
            g.close()
            return

if __name__ == "__main__":
    g:Game = Game()
    s = pygame.display.set_mode((1440*0.75,1080*0.75))
    getGameDataThread = threading.Thread(target=GameGetGameData, args=(g,))
    getGameDataThread.name = "get game data thread"
    getGameDataThread.daemon = True
    getGameDataThread.start()

    previousTime = time.time()
    while g.gameIsOn:
        timeNow = time.time()
        dt = timeNow - previousTime
        previousTime = timeNow
        handelPlayerMovement(g.gameEntity, dt)
        for e in pygame.event.get():
            if e.type == pygame.QUIT: g.close()
            if e.type == pygame.KEYUP:
                if e.key == pygame.K_q:
                    g.close()

        s.fill((0,0,0))
        es = [v for _,v in g.gameEntities.items()]
        drawGameEntities(s, g.gameEntities)
        pygame.display.flip()
        g.sendGameData()
    print("end loop")
    getGameDataThread.join()
