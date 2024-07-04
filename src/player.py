from typing import Any
import pygame
from pygame.math import Vector2
from sprites import Entity
from logger import log

class Player(Entity):
    def __init__(self) -> None:
        super().__init__(type="player")
        # no image yet
        self.image = pygame.image.load("assets/characters/char1/char1_idle.png").convert_alpha()
        self.rect = self.image.get_rect(center=(100, 100))
        self.__pos = pygame.Vector2((100, 100))
        log("Creates class player")

    def get_pos(self) -> pygame.Vector2:
        return pygame.Vector2(self.rect.centerx, self.rect.centery)

    def __move(self, *args, **kwargs) -> None:
        k = pygame.key.get_pressed()
        x = int(k[pygame.K_d]) - int(k[pygame.K_a])
        y = int(k[pygame.K_s]) - int(k[pygame.K_w])
        f: pygame.Vector2
        if x == 0 and y == 0:
            f = pygame.Vector2()
        else:
            f = pygame.Vector2((x, y)).normalize()
        s = self.speed
        if k[pygame.K_LSHIFT]: s = self.dash_speed
        self.velocity += f * s


    def update(self, dt) -> None:
        self.__move()
        self.__pos += self.velocity * dt
        self.rect.left = int(self.__pos.x)
        self.rect.top = int(self.__pos.y)
        self.rect.centerx = int(self.__pos.x)
        self.rect.centery = int(self.__pos.y)
        # log(f"Player position __pos: {str((self.__pos.x, self.__pos.y)): >10} rect: "
        #     f"{str((self.rect.left, self.rect.top)): >10}") 

        # collisions to also check for velocity
        self.velocity = pygame.Vector2((0, 0))

