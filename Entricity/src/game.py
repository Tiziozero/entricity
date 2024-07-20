from enum import Enum
from typing import final
from logger import *
import pygame, sys
from time import sleep

from sprite_groups import EntitySpritesGroup, GroundSpriteGroup, SpriteGroup
from player import Player
from characters import SoilderSide1, Wizart
from camera import Camera
from map import Map
from threading import Thread

from connections import Connections

class GameLoadingState(Enum):
    STATE_DONE = "done"
    STATE_ERROR = "error"
    STATE_LOADING = "loading"

class Game:
    def __init__(self) -> None:
        # Game Variebles
        self.conn : Connections
        self.screen = pygame.display.get_surface()    
        self.clock = pygame.time.Clock()
        self.WIDTH, self.HEIGHT = self.screen.get_size()
        
        # Game sprites/groups and player
        self.__all_sprites: SpriteGroup

        self.map: Map
        self.__ground_sprites: GroundSpriteGroup

        self.__object_sprites: EntitySpritesGroup

        self.__entity_sprites: EntitySpritesGroup
        self.__player: Player
        self.camera: Camera

        self.font: pygame.font.Font

        # Game flags
        self.game_is_on: bool = False
        self.game_error: Exception | None = None

        self.__setup()
    def set_conn(self, c: Connections) -> None:
        self.conn = c
        self.conn.send_stream_message('Blobolop in game')

    def __setup(self) -> None:
        self.loading_message = ""
        self.loading_state: GameLoadingState = GameLoadingState.STATE_LOADING
        self.font = pygame.font.Font("./assets/fonts/CascadiaCode/CaskaydiaCoveNerdFont-Regular.ttf", 30)

        self.lsi = pygame.image.load("./assets/loading_screen.jpg")
        self.lsi = pygame.transform.scale(self.lsi, (self.WIDTH, self.HEIGHT))
        def load(self):
            try:
                self.loading_message = "Making sprite groups..."
                self.__all_sprites = SpriteGroup()
                self.__ground_sprites = GroundSpriteGroup()
                self.__object_sprites = EntitySpritesGroup()
                self.__entity_sprites = EntitySpritesGroup()

        
                self.loading_message = "Making player..."
                # self.__player = SoilderSide1()
                self.__player = Wizart()
                self.camera = Camera(self.__player)
                self.__all_sprites.add(self.__player)
                self.__entity_sprites.add(self.__player)

                self.loading_message = "Initialising map group..."
                self.map = Map("xl_base")
                self.__ground_sprites.set_map(self.map)

            except Exception as e:
                err(f"Error in creating map: {e}")
                self.game_error = e
                self.loading_state = GameLoadingState.STATE_ERROR
                return
            finally:
                self.loading_message = "Done loading."
                self.loading_state = GameLoadingState.STATE_DONE
                log("Done Loading")



        load_th = Thread(target=load, args=[self,])
        load_th.daemon = True
        load_th.start()

        while self.loading_state != GameLoadingState.STATE_DONE:
            if self.loading_state == GameLoadingState.STATE_ERROR:
                if self.game_error:
                    raise self.game_error
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    sys.exit()
            # render text
            text = self.font.render(self.loading_message, True, (255, 255, 255))
            trect = text.get_rect(bottomright=self.screen.get_rect().bottomright)

            # self.screen.fill(color)
            self.screen.blit(self.lsi, (0, 0))
            self.screen.blit(text, trect)
            pygame.display.update()
        log("Finished loading")

        load_th.join()
        self.done_loading = True
        self.game_is_on = True
        return


    def display_fps(self):
        fps = self.clock.get_fps()
        fps_text = self.font.render(f"FPS: {fps:.2f}", True, pygame.Color('white'))
        self.screen.blit(fps_text, (10, 10))

    def __draw(self) -> None:
        self.screen.fill("white")
        self.__ground_sprites.dodraw(surface=self.screen, camera=self.camera)
        
        self.__entity_sprites.dodraw(surface=self.screen, camera=self.camera)
        self.display_fps()
        pygame.display.flip()

    def __update(self):
        dt: float = self.clock.tick(60) / 1000.0
        self.__all_sprites.update(dt)
        self.camera.update()

        self.__draw()

    def run(self) -> int:
        log("Running Game run")
        retval = 0
        while self.game_is_on:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.game_is_on = False
                    retval = -1  
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_p:
                        self.game_is_on = False
                        retval = 0
                    if e.key == pygame.K_ESCAPE:
                        self.game_is_on = False
                        retval = 0

            self.__update()
        self.__cleanup()
        return retval

    def __cleanup(self):
        for s in self.__all_sprites.sprites():
            s.image=None
        self.__player.image=None

