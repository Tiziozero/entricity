from re import S
from threading import Thread
from typing import List
import pygame

from logger import *
from sprite_groups import DrawSpriteGroup, GroundSpriteGroup, SpriteGroup
from player import Player
from camera import Camera
from map import Map
# from threading import Thread

# from connections import Connections

from scene import Scene
from constants import *
import connections, serialisation
from sprites import Entity


class Game(Scene):
    def __init__(self) -> None:
        super().__init__()
        # All sprites.
        self.__all_sprites:     SpriteGroup = SpriteGroup()

        # Server Sprites
        self.__server_sprites:  SpriteGroup = DrawSpriteGroup()
        # Sprites to draw
        self.__draw_sprites:    SpriteGroup = DrawSpriteGroup()
        # Sprites for collisions
        self.__collide_sprites: SpriteGroup = SpriteGroup()

        # Map. May include items not in server.
        self.__ground_sprites:  SpriteGroup = GroundSpriteGroup()
        
        self.player: Player
        self.camera: Camera =  Camera(None)

    def update(self) -> List[pygame.event.Event]:
        dt = self._clock.tick(60) / 1000.0
        for event in super().update():
            # handle extra events
            ...
        for s in self.__all_sprites:
            s.update(dt=dt)
        self.camera.update()
        return []

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill("black")
        self.__ground_sprites.draw(self.screen, self.camera)
        self.__draw_sprites.draw(self.screen, self.camera)
        for e in self.ui:
            e.draw(screen)
        pygame.display.flip()

    def get_game_data(self):
        if self._cfg.conn:
            while self.on:
                b = self._cfg.conn.receive_game_data()
                entities = serialisation.deserialise_entities(b)
                for entity in entities:
                    if entity.in_server_id == self.player.in_server_id:
                        continue
                    e = self.__all_sprites[entity.in_server_id]
                    if e == None:
                        # Add request to server for entity info and add entity
                        e = Entity()
                        e.in_server_id = entity.in_server_id
                        self.__all_sprites.add(e)
                        self.__draw_sprites.add(e)
                        continue
                    if entity.posX.changed:
                        e.state.pos.x = entity.posX.value
                    if entity.posY.changed:
                        e.state.pos.y = entity.posY.value
                    if entity.state.changed:
                        e.state.state = entity.state.value
                    if entity.direction.changed:
                        e.state.direction = entity.direction.value

        else:
            err("Server connection is not alive.")

    def start(self):
        log("Start")
        def __loader(self) -> str:
            try:
                map = Map()
                self.player = Player(CHARACTER_WIZART)

                self.__ground_sprites = GroundSpriteGroup(map)
                self.__draw_sprites.add(self.player)
                self.__all_sprites.add(self.player)
                self.camera =  Camera(self.player)

            except Exception as e:
                log(f"{e}")
                self._cfg.error = e
                return LOADING_STATE_ERROR 
            return LOADING_STATE_DONE
         
        self.load(__loader, None)
        if self._cfg.conn:
            game_data_thread = Thread(target=self.get_game_data)
            game_data_thread.daemon = True
            game_data_thread.name = "game_data_thread"
            game_data_thread.start()
        else: raise Exception("Failed to create game data thread. connection is not live.")

        log("End loading")
        if self._cfg.conn:
            while self.on:
                self.update()
                self.draw(self.screen)
                self._cfg.conn.send_game_data(self.player)
        game_data_thread.join()

if __name__ == "__main__":
    pygame.init()
    pygame.display.set_mode((1080, 810))
    g = Game()
    g.start()
