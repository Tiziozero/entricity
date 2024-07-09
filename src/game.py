from logger import *
import pygame, sys
from time import sleep

from sprite_groups import EntitySpritesGroup, GroundSpriteGroup, SpriteGroup
from player import Player
from characters import SoilderSide1, Wizart
from camera import Camera
from map import Map, CSVMap
from threading import Thread

class Game:
    def __init__(self) -> None:
        # Game Variebles
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
        self.done_loading: bool = False

        self.__setup()

    def __setup(self) -> None:
        self.loading_message = ""
        self.done_loading = False
        self.font = pygame.font.Font("./assets/fonts/CascadiaCode/CaskaydiaCoveNerdFont-Regular.ttf", 30)
        self.lsi = pygame.Surface((self.WIDTH, self.HEIGHT))
        self.lsi = pygame.image.load("./assets/loading_screen.jpg")
        self.lsi = pygame.transform.scale(self.lsi, (self.WIDTH, self.HEIGHT))
        def load(self):
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
            self.map = CSVMap()
            self.__ground_sprites.set_map(self.map)

            self.loading_message = "Done loading."
            self.done_loading=True
            log("Done Loading")


        load_th = Thread(target=load, args=[self,])
        load_th.daemon = True
        load_th.start()

        while not self.done_loading:
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

