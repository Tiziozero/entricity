from typing import Any
import pygame
from pygame.math import Vector2
import sprites
from constants import *
from logger import log

class Player(sprites.Entity):
    def __init__(self, character:str=CHARACTER_WIZART) -> None:
        super().__init__(type="player")
        # no image yet
        self.character:str = character
        log("Creates class player")

    def get_pos(self) -> pygame.Vector2:
        return pygame.Vector2(self.rect.centerx, self.rect.centery)


    def move(self, *args, **kwargs) -> None:
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
        self.state.velocity += f * s
