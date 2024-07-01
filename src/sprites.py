import pygame
from typing import List, Optional
from camera import Camera
from logger import log

class Sprite(pygame.sprite.Sprite):
    def __init__(self, groups: List[pygame.sprite.Group]=[], type:str ="any") -> None:
        super().__init__(*groups)
        # sprite type
        self.type: str = type
        # blitting image (could be a sprite sheet)
        self.image: pygame.Surface = pygame.Surface((0,0))
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
        self.speed: int = speed
        # velocity will be the final direction player will move (calculated by summing all the forces + movement)
        self.velocity: pygame.Vector2 = pygame.Vector2()
        # direction entity is moving (not necessarily faceing)
        self.direction: str = "right"
    def __move(self, *args, **kwargs) -> None:
        # for entity to move e.g. AI, keyboard movement, controler...
        ...

class SpriteGroup(pygame.sprite.Group):
    def __init__(self, sprites: List[Sprite]=[]) -> None:
        super().__init__(*sprites)
        # self.surface = pygame.display.get_surface()

    def draw(self, surface: pygame.Surface, camera: Optional[Camera]=None) -> None:
        if camera is None:
            camera = Camera()
        sprts = sorted(self.sprites(), key=lambda s: s.rect.y if s.type != "ground" else 1)
        for s in sprts:
            if hasattr(s, "rect") and hasattr(s, "image"):
                blit_rect = s.rect.copy()
                blit_rect.x -= camera.offset.x
                blit_rect.y -= camera.offset.y
                special_flags = s.special_flags if hasattr(s, "special_flags") else 0
                log(s.type)
                if hasattr(s, "area_rect") and s.area_rect:
                    surface.blit(s.image, blit_rect, s.area_rect, special_flags)
                else:
                    surface.blit(s.image, blit_rect, special_flags=special_flags)

