from functools import cache
from typing import List, Any
import pygame
from camera import Camera
from logger import log


class SpriteGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        log("Initialising Draw Group")
        self.__surface: pygame.surface.Surface = pygame.surface.Surface((0, 0))
        self.__camera: Camera = Camera(None)

    def set_dest_surf(self, __surface: pygame.surface.Surface) -> None:
        self.__surface = __surface
    def set_camera(self, __camera: Camera) -> None:
        self.__camera = __camera

    # @cache
    def sort_sprites(self) -> List[pygame.sprite.Sprite]:
        log("len of sprites " + str( len(self.sprites())))
        return sorted(self.sprites(), key=lambda s: s.rect.centerx if s.type != "ground" else 0)

    def draw(self) -> None:
        sprts = self.sort_sprites()
        for s in sprts:
            if hasattr(s, "image") and hasattr(s, "rect"):
                r = pygame.Rect(s.rect.x, s.rect.y, s.rect.w, s.rect.h)
                r.x -= int(self.__camera.offset.x if self.__camera else 0)
                r.y -= int(self.__camera.offset.y if self.__camera else 0)
                if hasattr(s, 'area_rect'):
                    self.__surface.blit(s.image, r, area=s.area_rect)
                    continue
                self.__surface.blit(s.image, r)

    def update(self, *args: Any, **kwargs: Any) -> None:
        return super().update(*args, **kwargs)

