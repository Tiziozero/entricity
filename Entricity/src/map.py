from enum import Enum
import time
import pygame, csv, array

from pytmx.pytmx import json

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
    SPECIAL_OBJECTS = "special_objects"

    @classmethod
    def get(cls, key):
        try:
            return cls[key.upper()]
        except KeyError:
            raise ValueError(f"Invalid MapType: {key}")


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
class Tileset:
    def __init__(self, tileset_path:str, t_width: int, t_height: int, ts_w: int, ts_h: int) -> None:
        self.tileset:pygame.Surface = pygame.image.load(tileset_path).convert_alpha()
        self.t_width = t_width
        self.t_height = t_height
        self.ts_w =ts_w
        self.ts_h =ts_h
class Layer:
    def __init__(self, tileset: Tileset, width:int, height:int) -> None:
        self.tileset: Tileset = tileset
        self.width = width
        self.height = height
        # Load Tiles here
        self.tiles: TILE_GRID = []

    def load_tiles(self, tiles: TILE_GRID) -> None:
        self.tiles = tiles
    def get_blit_tiles(self, camera: pygame.Rect) -> List[Tile] | None:
        w = camera.w // self.tileset.t_width  + 1 + 1 # 
        h = camera.h // self.tileset.t_height + 1 + 1 # j
        # the first  "+ 1" is to fill the screen when the left most tile
        # starts at the screen edge.
        # the second "+ 1" is there because when first tile is  bearly showing,
        # at the right there is still some space, this fills it

        start_x_i = camera.x // self.tileset.t_width
        start_y_i = camera.y // self.tileset.t_height
        # print(f"{w=}{h=}{w*self.t_width=}{h*self.t_height=}")
        tiles: List[Tile]=[]

        while start_y_i + h > len(self): h -= 1
        while start_x_i + w > len(self[0]): w -= 1
        if h < 0: h = 0
        if w < 0: w = 0

        for j in range(h):
            for i in range(w):
                tiles.append(self[start_y_i+j][start_x_i+i])
        return tiles
    def __getitem__(self, i) -> List[Tile]:
        return self.tiles[i]
    def __len__(self) -> int:
        return len(self.tiles)

# Maps will be automatically be picked up from dirrectories in "./assets/maps/"
# Each dirrectories must contain a "config.json" with the attributes:
# data{data about the map},
# layers{different laysers indexed by name},
# tileset{path to tileset and data}
# not for now though
class Map:
    # In future make map only the base and static object that can't be
    # be interracted with or can't change like rocks, water and stuff
    # Implement loading method that gets data from server and loads it
    # to map
    def __init__(self, map_:str="base") -> None:
        t = time.time()
        self.base_maps_path = "./assets/maps/"
        self.map_path = self.base_maps_path + map_
        if not self.map_path.endswith("/"):
            self.map_path += "/"


        self.config_file = self.map_path + "config.json"
        self.data: Dict
        try:
            with open(self.config_file, 'r') as f:
                self.data = json.load(f)
        except FileNotFoundError as e:
            print(f"Error: The file {self.config_file} was not found.")
            raise e
        except json.JSONDecodeError as e:
            print(f"Error: Failed to decode JSON from the file {self.config_file}.")
            raise e
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raise e

        # Tiles
        self.tiles: Dict[MapType, Layer] = {}
        self.tile_sets: Dict[str, Tileset] = {}


        # implement returning drawing indexes for tiles
        # in this array if fixed size to improve performance
        # and not havinf to reallocate memory each time
        # -- to implement
        rows, cols = 3, 4
        self.return_indexes_for_render = [array.array('i', [0] * cols) for _ in range(rows)]

        # Start loading map
        self.setup_map_data()
        total_t = time.time() - t
        log(f"Took {total_t} seconds to load map: {self.map_path}")

    def setup_map_data(self) -> None:
        map = self.data.get("map", [])
        if len(map) <= 0:
            raise KeyError("Map config file does not contain"
                           "map data/map data is invalid"
                           )

        layers = self.data.get("layers", [])
        if len(layers) <= 0:
            raise KeyError("Map Layer config file does not contain"
                           "map data/map data is invalid"
                           )
        tilesets = self.data.get("tilesets", [])
        if len(tilesets) <= 0:
            raise KeyError("Map Tilesets config file does not contain"
                           "map data/map data is invalid"
                           )
        # Work From tilesets, to layers
        for k, v in tilesets.items():
            tileset_path = self.map_path + v["filename"]
            tilewidth = v["tilewidth"]
            tileheight = v["tileheight"]
            ts_w = v["width"]
            ts_h = v["height"]
            self.tile_sets[k] = Tileset(
                    tileset_path=tileset_path,
                    t_width=tilewidth,
                    t_height=tileheight,
                    ts_w=ts_w,
                    ts_h=ts_h
                )
        for k, v in layers.items():
            fn = v["filename"]
            w = v["width"]
            h = v["height"]
            ts = v["tileset"]
            mt = MapType.get(k)
            self.tiles[mt] = Layer(width=w, height=h, tileset=self.tile_sets[ts])
            tiles = self.load_tiles(self.map_path + fn, self.tiles[mt].tileset)
            self.tiles[mt].load_tiles(tiles)



    def load_tiles(self, file_path:str, ts: Tileset) -> TILE_GRID:
        with open(file_path, "r") as f:
            # Good enough, will implement checking if valid later
            csv_map_data = csv.reader(f)

            return self.create_tiles([c for c in [r for r  in csv_map_data]], ts)

    def create_tiles(self, csv_map_data: List[List[str]], ts: Tileset) -> TILE_GRID:
        tiles: TILE_GRID = []
        for j in range(len(csv_map_data)):                # y axis map index
            r: List[Tile] = []
            for i in range(len(csv_map_data[j])):         # x axis map index
                tid = int(csv_map_data[j][i])
                tile_x_ = i * ts.t_width
                tile_y_ = j * ts.t_height
                blit_rect = pygame.Rect(
                    tile_x_,
                    tile_y_,
                    ts.t_width,
                    ts.t_height
                        )
                ts_area_rect_x_ = ts.t_width*(tid % ts.ts_w)
                ts_area_rect_y_ = ts.t_height*(tid // ts.ts_h)
                ts_area_rect_w_ = ts.t_width
                ts_area_rect_h_ = ts.t_height
                area_rect = pygame.Rect(
                    ts_area_rect_x_,
                    ts_area_rect_y_,
                    ts_area_rect_w_,
                    ts_area_rect_h_
                )
                t = GroundTile(tid, blit_rect, area_rect)
                r.append(t)
            tiles.append(r)
        return tiles

    def get_blit_tiles(self, camera: pygame.Rect, l: Layer) -> List[Tile] | None:
        w = camera.w // l.tileset.t_width  + 1 + 1 # 
        h = camera.h // l.tileset.t_height + 1 + 1 # j
        # the first  "+ 1" is to fill the screen when the left most tile
        # starts at the screen edge.
        # the second "+ 1" is there because when first tile is  bearly showing,
        # at the right there is still some space, this fills it

        start_x_i = camera.x // l.tileset.t_width
        start_y_i = camera.y // l.tileset.t_height
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
