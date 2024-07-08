import pygame

from sprites import Sprite
from typing import Dict, List, Tuple
from logger import log, err
from utils import divide_array_evenly, largest_common_factor_less_than_n

from pytmx.util_pygame import load_pygame
from threading import Thread



class Tile(Sprite):
    def __init__(self, groups: List[pygame.sprite.Group] = [], type:str="ground", tl =(0, 0)) -> None:
        super().__init__(groups=groups, type=type)

class GroundTile(Tile):
    def __init__(self,
                 x: int, y: int,
                 s: pygame.Surface,
                 groups: List[pygame.sprite.Group] = []) -> None:
        super().__init__(groups, type="ground")
        self.image = s
        self.rect = s.get_rect(topleft=(x, y))

class Map:
    def __init__(self, map:str="./assets/maps/base/base.tmx") -> None:
        # map will be drawn in 50x50 (*48) quadrants to minimise render time
        self.tiles: Dict = {}
        self.tiles["ground"]= []
        self.tiles["all"]= []

        self.tmx_data = load_pygame(map)
        # Tile size
        self.t_width: int = self.tmx_data.tilewidth
        self.t_height: int = self.tmx_data.tileheight
        # Map size (number of tiles)
        self.m_tw: int = self.tmx_data.width
        self.m_th: int = self.tmx_data.height
        self.m_width: int = self.m_tw * self.t_width
        self.m_height: int = self.m_th * self.t_height

        self.load_tmx_tiles()

        self.create_quadrants()
        log("Done creating quadrants")
        input()

    def get_map_tile(self) -> Tile:
        t = Tile()
        # t.image = self.map
        # t.rect = t.image.get_rect()
        return t

    def load_tmx_tiles(self) -> None:
        """
            This Method loads tiles from the tmx data

            get_layer_by_name returnes pytmx.TiledTileLayer
            method tiles() returns a tuple with (x, y, Surface)
            where:
                x is the column in the tiled map
                y is the row    in the tiled map
                Surface is the surface itself/image
            creates n loading threads that concurrently create
            tiless from provided tmx data
        """
        t = [h for h in self.tmx_data.get_layer_by_name("ground").tiles()]
        self.tiles_data_length = len(t)

        log(f"Loading {self.tiles_data_length=} tiles...")
        self.loading_threads_n = 200
        self.tile_slices = divide_array_evenly(t, self.loading_threads_n)
        threads = []
        for s in self.tile_slices:
            th = Thread(target=self.load_tiles_from_slice, args=(s, "ground"))
            th.daemon = True
            th.start()
            threads.append(th)
        for th in threads:
            th.join()
        """
        self.map = pygame.Surface((self.m_width, self.m_height))
        for t in self.tiles["ground"]:
            if t.image:
                self.map.blit(t.image, t.rect)
        """

    def load_tiles_from_slice(self,
            slice: List[Tuple[int, int, pygame.Surface]],
            tiles_class: str
        ) -> None:
        try:
            for x, y, s in slice:
                t= GroundTile(x* self.t_width, y*self.t_height, s)
                self.tiles["all"].append(t)
                self.tiles[tiles_class].append(t)
        except ValueError as ve:
            err(f"Error in loading map: {ve}")
        except Exception as e:
            err(f"Error in loading map: {e}")

    """
    def create_quadrants(self) -> None:
        self.llcf = 50
        self.lcf = largest_common_factor_less_than_n(self.m_tw, self.m_th, self.llcf)
        if not self.lcf:
            raise ValueError(f"Couldn't find largest common factor less than {self.llcf} for the values {self.m_tw} and {self.m_th}")

        self.quadrants_x: int = self.m_width // (self.t_width*self.lcf)
        self.quadrants_y: int = self.m_height // (self.t_height*self.lcf)
        self.quadrants_width: int = self.lcf*self.t_width
        self.quadrants_height: int = self.lcf*self.t_height 
        log(f"{self.quadrants_x}:{self.quadrants_y}")
        self.map_ground_tiles: List[List[GroundTile]] = []
        for j in range(self.m_th // self.lcf): # y axis index
            row: List[GroundTile] = []
            for i in range(self.m_tw // self.lcf): # x axis index
                x, y = i * self.quadrants_width, j * self.quadrants_height
                w, h = self.quadrants_width, self.quadrants_height

                r = pygame.Rect(x, y, w, h)
                log(f"{(r.x, r.y, r.w, r.h)}")
                s = self.map.subsurface(r)
                gt = GroundTile(x, y, s)

                row.append(gt)
            self.map_ground_tiles.append(row)
    """
    def get_ground_tile(self, r: pygame.Rect) -> List[GroundTile] | None:
        x_index = r.x // self.quadrants_width
        y_index = r.y // self.quadrants_height
        try:
            t = self.map_ground_tiles[y_index][x_index]
            t1 = self.map_ground_tiles[y_index+1][x_index]
            t2 = self.map_ground_tiles[y_index+1][x_index+1]
            t3 = self.map_ground_tiles[y_index][x_index+1]
            # log(f"{(t.rect)}")
            return [t, t1, t2, t3]
        except Exception as e:
            err(f"Error in getting ground tile: {e}")
            return None
    def create_quadrants(self) -> None:
        self.llcf = 50
        self.lcf = largest_common_factor_less_than_n(self.m_tw, self.m_th, self.llcf)
        if not self.lcf:
            raise ValueError(f"Couldn't find largest common factor less than {self.llcf} for the values {self.m_tw} and {self.m_th}")

        self.quadrants_x: int = self.m_width // (self.t_width*self.lcf)
        self.quadrants_y: int = self.m_height // (self.t_height*self.lcf)
        self.quadrants_width: int = self.lcf*self.t_width
        self.quadrants_height: int = self.lcf*self.t_height 
        log(f"{self.quadrants_x}:{self.quadrants_y}")
        self.map_ground_tiles: List[List[GroundTile]] = []
        round = 0
        rs: Dict = {}
        ths = []
        for j in range(self.m_th // self.lcf): # y axis index
            th = Thread(target=self._make_quadrant_row, args=(j, rs))
            th.daemon = True
            th.start()
            ths.append(th)
            log(f"Started thread {j}...")
        for j, t in enumerate(ths):
            t.join()
            log(f"Thread {j} ended.")
        for k,_ in rs.items():
            log(f"key in dict: {k=}")
        self.map_ground_tiles = [rs[i] for i in range(len(rs))]

    def _make_quadrant_row(self, j: int, dict_) -> None:
        row: List[GroundTile] = []
        if not self.lcf: raise ValueError("Lowest common factor is None/ not found")
        for i in range(self.m_tw // self.lcf): # x axis index
            x, y = i * self.quadrants_width, j * self.quadrants_height
            w, h = self.quadrants_width, self.quadrants_height
            a = self.get_tiles_in_range(x, y, w, h)

            r = pygame.Rect(x, y, w, h)
            s = pygame.Surface((self.quadrants_width, self.quadrants_height))
            for t in a:
                s.blit(t.image, (t.rect.x - i * self.quadrants_width, t.rect.y - j * self.quadrants_height))
            gt = GroundTile(x, y, s)

            row.append(gt)
        dict_[j] = row

    def get_tiles_in_range(self, x, y, w, h):
        a = []
        for t in self.tiles["ground"]:
            if t.rect.left >= x and t.rect.right <= x+w:
                if t.rect.top >= y and t.rect.bottom <= y + h:
                    a.append(t)
        return a
