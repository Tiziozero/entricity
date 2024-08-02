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


class Game(Scene):
    def __init__(self) -> None:
        super().__init__()
        self.__all_sprites:     SpriteGroup = SpriteGroup()
        self.__draw_sprites:    SpriteGroup = DrawSpriteGroup()
        self.__collide_sprites: SpriteGroup = SpriteGroup()
        self.__ground_sprites:  SpriteGroup = GroundSpriteGroup()
        
        self.__object_sprites:  SpriteGroup = SpriteGroup()
        self.__entities_sprites:SpriteGroup = SpriteGroup()
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

    def start(self):
        log("Start")
        def __loader(self) -> str:
            try:
                map = Map()
                self.__ground_sprites
                self.player = Player(CHARACTER_WIZART)
                self.__ground_sprites = GroundSpriteGroup(map)
                self.__entities_sprites.add(self.player)
                self.__draw_sprites.add(self.player)
                self.__all_sprites.add(self.player)
                self.camera =  Camera(self.player)

            except Exception as e:
                log(f"{e}")
                self._cfg.error = e
                return LOADING_STATE_ERROR 
            return LOADING_STATE_DONE
         
        self.load(__loader, None)
        log("End loading")
        while self.on:
            self.update()
            self.draw(self.screen)

if __name__ == "__main__":
    pygame.init()
    pygame.display.set_mode((1080, 810))
    g = Game()
    g.start()
