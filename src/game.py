from logger import *
import pygame

from sprites import SpriteGroup
from player import Player
class Game:
    def __init__(self) -> None:
        self.screen = pygame.display.get_surface()    
        self.clock = pygame.time.Clock()
        
        self.__all_sprites: SpriteGroup = SpriteGroup()
        self.__player: Player = Player()
        self.__all_sprites.add(self.__player)

    def __draw(self) -> None:
        self.screen.fill("white")
        self.__all_sprites.draw(surface=self.screen)
        pygame.display.flip()

    def __update(self):
        dt: float = self.clock.tick(60) / 1000.0
        self.__all_sprites.update(dt)

        self.__draw()

    def run(self) -> None:
        log("Running Game run")
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_p:
                        return

            self.__update()
