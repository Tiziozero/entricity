import pygame
from typing import List, Optional
from camera import Camera
from logger import log
from sprites import Sprite

class SpriteGroup(pygame.sprite.Group):
    def __init__(self, sprites: Optional[List[Sprite]] = None) -> None:
        if sprites: super().__init__(*sprites)
        else: super().__init__()
        # self.surface = pygame.display.get_surface()

    def dodraw(self, surface: pygame.Surface, camera: Optional[Camera]=None) -> None:
        if camera is None:
            camera = Camera(None)
        sprts = sorted(self.sprites(), key=lambda s: s.rect.y if s.type != "ground" else 1)
        for s in sprts:
            if hasattr(s, "rect") and hasattr(s, "image"):
                blit_rect = s.rect.copy()
                blit_rect.x -= int(camera.offset.x)
                blit_rect.y -= int(camera.offset.y)
                special_flags = s.special_flags if hasattr(s, "special_flags") else 0
                if hasattr(s, "area_rect") and s.area_rect and False:
                    surface.blit(s.image, blit_rect, s.area_rect, special_flags)
                else:
                    surface.blit(s.image, blit_rect, special_flags=special_flags)

