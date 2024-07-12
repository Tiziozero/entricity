from typing import Any
import pygame
from pygame.math import Vector2
from sprites import Entity
from logger import log
from game_enums import EntityDirections, EntityStates
class Player(Entity):
    def __init__(self) -> None:
        super().__init__(type="player")
        # no image yet
        self.image = pygame.Surface((0,0), 0xffffff)
        self.rect = self.image.get_rect()
        self.pos = pygame.Vector2((100, 100))
        log("Creates class player")

    def get_pos(self) -> pygame.Vector2:
        return pygame.Vector2(self.rect.centerx, self.rect.centery)

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
        # set FACING direction
        if self.velocity.y > 0: self.facing = EntityDirections.DOWN
        elif self.velocity.y < 0: self.facing = EntityDirections.UP
        if self.velocity.x > 0: self.facing = EntityDirections.RIGHT
        elif self.velocity.x < 0: self.facing = EntityDirections.LEFT
        
        # set state based on velocity from player
        if self.velocity.length() > 0:
            self.state = EntityStates.WALKING
        else:
            self.state = EntityStates.IDLE


    def update(self, dt) -> None:
        self.__move()
        self.pos += self.velocity * dt
        self.rect.left = int(self.pos.x)
        self.rect.top = int(self.pos.y)
        self.rect.centerx = int(self.pos.x)
        self.rect.centery = int(self.pos.y)
        # log(f"Player position pos: {str((self.pos.x, self.pos.y)): >10} rect: "
        #     f"{str((self.rect.left, self.rect.top)): >10}") 

        # collisions to also check for velocity
        self.velocity = pygame.Vector2((0, 0))

