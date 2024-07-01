from typing import List
from logger import err, log, warn
import pygame
from entity import Entity
import csv
class Obstacles:
    def __init__(self) -> None:
        pass
class Tile(Entity):
    def __init__(
            self,
            t: int,
            img: pygame.Surface,
            area_rect: pygame.Rect,
            blit_rect: pygame.Rect,
            groups: List[pygame.sprite.Group]=[]
                 ) -> None:
        super().__init__(*groups)
        self.is_ground = True
        self.type = "ground"
        self.gtype = t
        self.image: pygame.Surface = img
        self.rect: pygame.Rect = blit_rect
        self.area_rect: pygame.Rect = area_rect

class Map:
    def __init__(self, map_:str='base', groups: List[pygame.sprite.Group]=[]) -> None:
        self.groups = groups
        self.floor: list[Tile]
        self.obstacles: list[Obstacles]
        self.map_name: str = map_
        self.tile_map: list[list[int]] = []
        self.tile_set: pygame.Surface
        self.tile_map_x_n: int
        self.tile_map_y_n: int
        self.tile_size: int = 48
        self.tiles: list[pygame.sprite.Sprite] = []
        if not self.__setup():
            warn(f"\"{self.map_name}\" is not a valid map.")
            raise ValueError(f"\"{self.map_name}\" is not a valid map.")

    def __setup(self) -> bool:
        try:
            self.tile_set = pygame.image.load("./assets/maps/base/tile_set.png")
            temp_r = self.tile_set.get_rect()
            self.tile_map_x_n = temp_r.width // self.tile_size
            self.tile_map_y_n = temp_r.height // self.tile_size
             
            with open("./assets/maps/base/base_ground.csv", "r") as f:
                csv_reader = csv.reader(f)
                for r in csv_reader:
                    row_: list[int] = []
                    for c in r:
                        row_.append(int(c))
                    self.tile_map.append(row_)

            for i, r in enumerate(self.tile_map):
                for j, c in enumerate(r):
                    y = c // self.tile_map_y_n
                    x = c % self.tile_map_x_n
                    blit_rect = pygame.Rect(
                            j * self.tile_size,
                            i * self.tile_size,
                            self.tile_size,
                            self.tile_size)
                    area_rect = pygame.Rect(
                            x * self.tile_size,
                            y * self.tile_size,
                            self.tile_size,
                            self.tile_size
                            )
                    self.tiles.append(Tile(c, self.tile_set, area_rect, blit_rect, groups=self.groups))

        except Exception as e:
            err(f"An error occured in Map method __setup: {e}")
            return False

        return True

    def get_tiles(self) -> List[pygame.sprite.Sprite] :
        return self.tiles
