from logger import *
import pygame, sys
from time import sleep

from sprite_groups import SpriteGroup
from player import Player
from camera import Camera
from map import Tile
from threading import Thread
class Game:
    def __init__(self) -> None:
        # Game Variebles
        self.screen = pygame.display.get_surface()    
        self.clock = pygame.time.Clock()
        
        # Game sprites/groups and player
        self.__all_sprites: SpriteGroup
        self.__player: Player
        self.camera: Camera

        self.font: pygame.font.Font

        # Game flags
        self.game_is_on: bool = False
        self.done_loading: bool = False
        self.__setup()

    def __setup(self) -> None:
        self.loading_message = ""
        self.done_loading = False
        self.font = pygame.font.Font(None, 42)
        def load(self):
            self.loading_message = "Making sprite groups..."
            self.__all_sprites = SpriteGroup()
            sleep(2)

            self.loading_message = "Making player..."
            self.__player = Player()
            self.camera = Camera(self.__player)
            sleep(2)

            self.loading_message = "Initialising sprite groups..."
            self.__all_sprites.add(self.__player)
            self.__all_sprites.add(Tile())
            sleep(2)

            self.loading_message = "Loading player data..."
            sleep(5)
            self.loading_message = "Loading ur mom's pussy..."
            sleep(2)
            self.done_loading=True
            log("Done Loading")


        load_th = Thread(target=load, args=[self,])
        load_th.daemon = True
        load_th.start()

        color = 0x000000
        d =0
        while not self.done_loading:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    sys.exit()
            # render text
            text = self.font.render(self.loading_message, True, (255, 255, 255))
            trect = text.get_rect(bottomright=self.screen.get_rect().bottomright)

            self.screen.fill(color)
            self.screen.blit(text, trect)
            pygame.display.update()
            # d += 1
            # if d % 200 == 0:
            #     color += 0x010101
            #     log(color)
        log("Finished loading")

        load_th.join()
        self.done_loading = True
        self.game_is_on = True
        return


    def __draw(self) -> None:
        self.screen.fill("white")
        self.__all_sprites.dodraw(surface=self.screen, camera=self.camera)
        pygame.display.flip()

    def __update(self):
        dt: float = self.clock.tick(60) / 1000.0
        self.__all_sprites.update(dt)
        self.camera.update()

        self.__draw()

    def run(self) -> None:
        log("Running Game run")
        while self.game_is_on:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.game_is_on = False
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_p:
                        self.game_is_on = False

            self.__update()
        self.__cleanup()

    def __cleanup(self):
        for s in self.__all_sprites.sprites():
            s.image=None
        self.__player.image=None

