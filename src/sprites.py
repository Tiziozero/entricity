import pygame
from typing import List, Optional
from camera import Camera
from logger import log

class Sprite(pygame.sprite.Sprite):
    def __init__(self, groups: List[pygame.sprite.Group]=[], type:str ="any") -> None:
        super().__init__(*groups)
        self.type: str = type
        self.image: pygame.Surface
        self.rect: pygame.Rect
        self.area_rect: pygame.Rect
        self.special_blit_flags: int

    def _setup(self) -> None:
        self.image = pygame.Surface((0,0))
        self.rect = self.image.get_rect()

class SpriteGroup(pygame.sprite.Group):
    def __init__(self, sprites: List[Sprite]=[]) -> None:
        super().__init__(*sprites)

    def draw(self, surface: pygame.Surface, camera: Optional[Camera]=None) -> None:
        if camera is None:
            camera = Camera()
        sprts = sorted(self.sprites(), key=lambda s: s.rect.x if s.type != "ground" else 1)
        for s in sprts:
            if hasattr(s, "rect") and hasattr(s, "image"):
                blit_rect = s.rect.copy()
                blit_rect.x -= camera.offset.x
                blit_rect.y -= camera.offset.y
                area_rect = s.area_rect if hasattr(s, "area_rect") else None
                special_flags = s.special_flags if hasattr(s, "special_flags") else 0
                surface.blit(s.image, blit_rect, area_rect, special_flags)

