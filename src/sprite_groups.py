import pygame
from typing import List, Optional
from camera import Camera
from logger import log, err
from sprites import Sprite
from player import Player
from map import Map

class SpriteGroup(pygame.sprite.Group):
    def __init__(self, sprites: Optional[List[Sprite]] = None) -> None:
        if sprites: super().__init__(*sprites)
        else: super().__init__()
        # self.surface = pygame.display.get_surface()

    """
    def dodraw(self, surface: pygame.Surface, camera: Optional[Camera]=None) -> None:
        if camera is None:
            camera = Camera(None)
        sprts = sorted(self.sprites(), key=lambda s: s.rect.centery if s.type != "ground" else 1)
        for s in sprts:
            if hasattr(s, "rect") and hasattr(s, "image"):
                blit_rect = s.rect.copy()
                blit_rect.x -= int(camera.offset.x)
                blit_rect.y -= int(camera.offset.y)
                special_flags = s.special_flags if hasattr(s, "special_flags") else 0
                pygame.draw.rect(surface, 0xff0000, blit_rect, 1)
                if hasattr(s, "area_rect") and s.area_rect and False:
                    surface.blit(s.image, blit_rect, s.area_rect, special_flags)
                else:
                    surface.blit(s.image, blit_rect, special_flags=special_flags)
    """

def can_draw(draw_rect: pygame.Rect, c: Camera)->bool:
    if draw_rect.bottom < c.top or draw_rect.top > c.bottom:
        return False
    if draw_rect.right < c.left or draw_rect.left > c.right:
        return False
    return True


def can_draw_original_pos(r :pygame.Rect, c: Camera) -> bool:
    if r.right < c.left or r.left > c.right:
        return False
    if r.top > c.bottom or r.bottom < c.top:
        return False
    return True
class EntitySpritesGroup(SpriteGroup):
    def __init__(self, sprites: Optional[List[Sprite]] = None) -> None:
        super().__init__(sprites)
    def dodraw(self, surface: pygame.Surface, camera: Optional[Camera]=None) -> None:
        if camera is None:
            camera = Camera(None)
        sprts = sorted(self.sprites(), key=lambda s: s.rect.centery)
        for s in sprts:
            if hasattr(s, "rect") and hasattr(s, "image"):
                if not can_draw_original_pos(s.rect, camera):
                    continue
                blit_rect = s.rect.copy()
                blit_rect.x -= int(camera.offset.x)
                blit_rect.y -= int(camera.offset.y)
                special_flags = s.special_flags if hasattr(s, "special_flags") else 0
                pygame.draw.rect(surface, 0xff0000, blit_rect, 1)
                # Entities should not have a area rect
                surface.blit(s.image, blit_rect, special_flags=special_flags)


class GroundSpriteGroup(SpriteGroup):
    def __init__(self, map: Map|None = None) -> None:
        super().__init__()
        self.map = map

    def set_map(self, map: Map) -> None:
        self.map = map

    def dodraw(self, surface: pygame.Surface, camera: Optional[Camera]=None) -> None:
        if not self.map:
            raise ValueError("Map is missing.")
        blitted = 0
        if camera is None:
            camera = Camera(None)
        tiles = self.map.get_ground_tiles(camera.rect)
        if not tiles:
            err("No tiles")
            return
        for t in tiles:
            if t.blit_rect:
                blit_rect = t.blit_rect.copy()
                blit_rect.x -= int(camera.offset.x)
                blit_rect.y -= int(camera.offset.y)
                surface.blit(self.map.tile_set, blit_rect, t.area_rect)
                pygame.draw.rect(surface, 0xff0000, blit_rect, 1)
                blitted += 1
        # log(f"Blitted: {blitted} tiles")

