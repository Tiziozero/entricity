import pygame
from typing import Dict, Optional
from camera import Camera
from logger import log, warn, err
from sprites import Sprite
from map import Map, MapType

class SpriteGroup:
    def __init__(self, *sprites: Sprite) -> None:
        self._sprites: Dict[int,Sprite] = {}
        for s in sprites:
            self._sprites[s.in_server_id] = s
            s.groups.append(self)  # Add this group to the sprite's list of groups
        ...

    def sprites(self):
        return self._sprites

    def get_from_in_server_id(self, isid) -> Sprite|None:
        return self._sprites.get(isid, None)

    def add(self, s: Sprite) -> None:
        if s not in self._sprites:
            self._sprites[s.in_server_id] = s
            s.groups.append(self)
            log(f"Added: {s}")
        else:
            log(f"{s} already in sprites")

    def remove(self, s: Sprite) -> None:
        self._sprites.__delitem__(s.in_server_id)
        s.groups.remove(self)  # Remove this group from the sprite's list of groups
        log(f"Removed: {s}")
    def __iter__(self):
        return iter(self._sprites.values())
    def __getitem__(self, i) -> Sprite|None:
        return self._sprites.get(i, None)
    def __setitem__(self, i:int, v:Sprite):
        self._sprites[i]=v

    def __len__(self):
        return len(self._sprites)

    def draw(self, screen: pygame.Surface, *args, **kwargs) -> None:
        ...

    def update(self, *args, **kwargs) -> None:
        for _, s in self._sprites.items():
            s.update(*args, **kwargs)

def can_draw_original_pos(r :pygame.Rect, c: Camera) -> bool:
    if r.right < c.left or r.left > c.right:
        return False
    if r.top > c.bottom or r.bottom < c.top:
        return False
    return True

class DrawSpriteGroup(SpriteGroup):
    def __init__(self, *sprites: Sprite) -> None:
        super().__init__(*sprites)
        self.warn_no_camra = False

    # Ignore errors
    def draw(self, surface: pygame.Surface, camera: Optional[Camera]=None) -> None:
        if camera is None:
            if not self.warn_no_camra:
                self.warn_no_camra = True
                warn("No camera for DrawSpriteGroup")
            camera = Camera(None)
        
        sprts = sorted(self._sprites.values(), key=lambda s: s.rect.centery)
        for s in sprts:
            try:
                blit_rect = s.rect.copy()

                blit_rect.x -= int(camera.offset.x)
                blit_rect.y -= int(camera.offset.y)
                special_flags = 0

                pygame.draw.rect(surface, 0xff0000, blit_rect, 1)

                # Sprites should not have a area rect
                surface.blit(s.sprite_sheet.image, blit_rect, special_flags=special_flags)
            except Exception as e:
                print(f"{e}")

class GroundSpriteGroup(SpriteGroup):
    def __init__(self, map: Map|None = None) -> None:
        super().__init__()
        self.map = map

    def draw(self, surface: pygame.Surface, camera: Optional[Camera]=None) -> None:
        if not self.map:
            raise ValueError("Map is missing.")

        if camera is None:
            camera = Camera(None)

        layer = self.map.tiles[MapType.GROUND]
        tiles = layer.get_blit_tiles(camera.rect)
        if not tiles:
            err("No tiles")
            return
        for t in tiles:
            if t.blit_rect:
                blit_rect = t.blit_rect.copy()
                blit_rect.x -= int(camera.offset.x)
                blit_rect.y -= int(camera.offset.y)
                surface.blit(layer.tileset.tileset, blit_rect, t.area_rect)
                # pygame.draw.rect(surface, 0xff0000, blit_rect, 1)
