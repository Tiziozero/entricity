import pygame
from sprites import Sprite
from logger import log

class Player(Sprite):
    def __init__(self) -> None:
        super().__init__(type="player")
        self.image = pygame.image.load("assets/characters/char1/char1_idle.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.pos = pygame.Vector2()
        log("Creates class player")
