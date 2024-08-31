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
        self.rect = pygame.Rect(self.offset, self.screen_size)
    @property
    def top(self):
        top = self.offset.y
        return top
    @property
    def bottom(self):
        bottom = self.offset.y + self.screen_size.y
        return bottom
    @property
    def left(self):
        left = self.offset.x
        return left
    @property
    def right(self):
        right = self.offset.x + self.screen_size.x
        return right
    def get_pos(self) -> pygame.Vector2:
        return pygame.Vector2(self.rect.centerx, self.rect.centery)

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
            self.rect.x, self.rect.y = int(self.offset.x), int(self.offset.y)
