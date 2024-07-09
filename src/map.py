from enum import Enum
import pygame, csv, array

from sprites import Sprite
from typing import Dict, List, Tuple
from logger import log, err
from utils import divide_array_evenly, largest_common_factor_less_than_n

from pytmx.util_pygame import load_pygame
from threading import Thread


class MapType(Enum):
    ALL = "all"
    GROUND = "ground"
    BASIC_OBJECTS = "basic_objects"


# Tile will NOT inherrit from sprite since it will only need a rect and area rect
# This will save memory and probably positivly impact performance
class Tile:
    def __init__(self) -> None:
        self.blit_rect: pygame.Rect = pygame.Rect(0,0,0,0)
        self.area_rect: pygame.Rect = pygame.Rect(0,0,0,0)
        ...
        
class GroundTile(Tile):
    def __init__(self, tid: int, blit_rect: pygame.Rect, area_rect: pygame.Rect) -> None:
        self.tid = tid
        self.blit_rect = blit_rect
        self.area_rect = area_rect
        ...

TILE_GRID = List[List[Tile]]
# Maps will be automatically be picked up from dirrectories in "./assets/maps/"
# Each dirrectories must contain a "config.json" with the attributes:
# data{data about the map},
# layers{different laysers indexed by name},
# tileset{path to tileset and data}
# not for now though
class Map:
    def __init__(self, map: str="") -> None:
        self.tiles: Dict[MapType, TILE_GRID] = {}
        self.tiles[MapType.ALL]= []
        self.tiles[MapType.GROUND]= []
        self.tile_set: pygame.Surface
    def get_ground_tiles(self, camera: pygame.Rect) -> List[Tile] | None:
        pass
class CSVMap(Map):
    def __init__(self, map:str="./assets/maps/base/base_ground.csv") -> None:
        super().__init__(map)
        self.map_path: str = map
        # Tiles

        # Tile Data (Must be hard coded)
        self.t_width: int = 48
        self.t_height: int = 48
        # Map Data (Must be hard coded)
        self.m_tw: int = 100
        self.m_th: int = 100
        self.m_width: int = self.m_tw * self.t_width
        self.m_height: int = self.m_th * self.t_height
        
        # Tile Set Data
        self.tile_set: pygame.Surface = pygame.image.load(
                "./assets/maps/base/tile_set.png"
                ).convert_alpha()
        ts_w, ts_h = self.tile_set.get_size()
        self.tile_set_x: int = ts_w // self.t_width
        self.tile_set_y: int = ts_h // self.t_height

        # return array for data:
        rows, cols = 3, 4
        self.return_indexes_for_render = [array.array('i', [0] * cols) for _ in range(rows)]


        # Start loading map
        self.load_map()

    def load_map(self) -> None:
        with open(self.map_path, "r") as f:
            # Good enough, will implement checking if valid later
            csv_map_data = csv.reader(f)

            self.create_tiles([c for c in [r for r  in csv_map_data]])

    def create_tiles(self, csv_map_data: List[List[str]]) -> None:
        # height largest common factor
        self.maxlcf = 50
        # finds largest common factor
        self.lcf = largest_common_factor_less_than_n(self.m_tw, self.m_th, self.maxlcf)
        if not self.lcf:
            raise ValueError(f"Couldn't find largest common factor less than {self.maxlcf} for the values {self.m_tw} and {self.m_th}")

        # number of quadrants in x and y
        self.quadrants_x: int = self.m_width // (self.t_width*self.lcf)
        self.quadrants_y: int = self.m_height // (self.t_height*self.lcf)
        # quadrants info
        self.quadrants_width: int = self.lcf*self.t_width
        self.quadrants_height: int = self.lcf*self.t_height 

        for j in range(len(csv_map_data)):  # y axis map index
            r: List[Tile] = []
            for i in range(len(csv_map_data[j])):         # x axis map index
                tid = int(csv_map_data[j][i])
                tile_x_ = i * self.t_width
                tile_y_ = j * self.t_height
                blit_rect = pygame.Rect(
                    tile_x_,
                    tile_y_,
                    self.t_width,
                    self.t_height
                        )
                ts_area_rect_x_ = self.t_width*(tid % self.tile_set_x)
                ts_area_rect_y_ = self.t_height*(tid // self.tile_set_y)
                ts_area_rect_w_ = self.t_width
                ts_area_rect_h_ = self.t_height
                area_rect = pygame.Rect(
                    ts_area_rect_x_,
                    ts_area_rect_y_,
                    ts_area_rect_w_,
                    ts_area_rect_h_
                )
                t = GroundTile(tid, blit_rect, area_rect)
                r.append(t)
            self.tiles[MapType.GROUND].append(r)

    def get_ground_tiles(self, camera: pygame.Rect) -> List[Tile] | None:
        w = camera.w // self.t_width  + 1 + 1 # 
        h = camera.h // self.t_height + 1 + 1 # j
        # the first  "+ 1" is to fill the screen when the left most tile
        # starts at the screen edge.
        # the second "+ 1" is there because when first tile is  bearly showing,
        # at the right there is still some space, this fills it

        start_x_i = camera.x // self.t_width
        start_y_i = camera.y // self.t_height
        # print(f"{w=}{h=}{w*self.t_width=}{h*self.t_height=}")
        ts = self.tiles[MapType.GROUND]
        tiles: List[Tile]=[]

        while start_y_i + h > len(ts): h -= 1
        while start_x_i + w > len(ts[0]): w -= 1
        if h < 0: h = 0
        if w < 0: w = 0

        for j in range(h):
            for i in range(w):
                tiles.append(ts[start_y_i+j][start_x_i+i])
        return tiles
