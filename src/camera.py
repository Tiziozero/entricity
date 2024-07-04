import pygame
from player import Player
from logger import log

class Camera:
    def __init__(self, playerRef: Player | None) -> None:
        # Should be alighed with topleft of player
        self.offset: pygame.Vector2 = pygame.Vector2()
        self.player_ref: Player | None = playerRef
        s = pygame.display.get_surface().get_rect()
        self.screen_size = pygame.Vector2(s.w, s.h)

    def __in_map_boundary(self, map) -> None:
        if self.player_ref:
            if self.offset.x < 0: self.offset.x = 0
            if self.offset.y < 0: self.offset.y = 0
            ...
    def update(self):
        # Check if cammera is within map bounds (which will be decided with a potential map class or smth)
        if self.player_ref:
            self.offset = self.player_ref.get_pos() - self.screen_size / 2
            self.__in_map_boundary(None)
        ...
