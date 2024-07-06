import pygame
from sprites import Sprite
from typing import List
import pytmx



class Tile(Sprite):
    def __init__(self, groups: List[pygame.sprite.Group] = []) -> None:
        super().__init__(groups=groups, type="ground")
        # self.image = pygame.image.load("")
        self.image = pygame.Surface((0,0))
        self.rect = self.image.get_rect()
        self.type="ground"

class Map:
    def __init__(self) -> None:
        tmx_data = pytmx.TiledMap('./assets/maps/base/base.tmx')

        print(f"Map width: {tmx_data.width} tiles")
        print(f"Map height: {tmx_data.height} tiles")
        print(f"Tile width: {tmx_data.tilewidth} pixels")
        print(f"Tile height: {tmx_data.tileheight} pixels")
