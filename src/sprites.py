import pygame
from typing import List

class Sprite(pygame.sprite.Sprite):
    def __init__(self, groups: List[pygame.sprite.Group]=[], type:str ="any") -> None:
        super().__init__(*groups)
        # sprite type
        self.type: str = type
        # blitting image (could be a sprite sheet)
        self.image: pygame.Surface | None = pygame.Surface((0,0))
        # rect in which sprite will be drawn/interracted with
        self.rect: pygame.Rect = self.image.get_rect()
        # area of image (sprite sheet which will be drawn)
        self.area_rect: pygame.Rect = self.image.get_rect()
        # special flags idk yet
        self.special_blit_flags: int = 0

class Entity(Sprite):
    def __init__(self, name:str="Unamed Entity", speed: int=200, groups: List[pygame.sprite.Group] = [], type: str = "any") -> None:
        super().__init__(groups, type)
        self.name: str = name
        
        # direction entity is faceing (for animations) not direction it's moving
        self.__facing: str = "right"

        # entity position
        self.pos: pygame.Vector2 = pygame.Vector2()
        # speed by which entity moves
        self.speed: float = speed
        self.dash_speed: float = speed * 3.5
        # velocity will be the final direction player will move (calculated by summing all the forces + movement)
        self.velocity: pygame.Vector2 = pygame.Vector2()
        # direction entity is moving (not necessarily faceing)
        self.direction: str = "right"
    def __move(self, *args, **kwargs) -> None:
        # for entity to move e.g. AI, keyboard movement, controler...
        ...

