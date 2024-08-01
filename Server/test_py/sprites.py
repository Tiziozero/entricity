import pygame
from typing import List, Any, Tuple
from constants import *

from animations import Animation

class Sprite:
    def __init__(self, groups: List[pygame.sprite.Group]=[], type:str ="any") -> None:
        super().__init__(*groups)
        #                 SpriteGroup but import cycle so... ye
        self.groups: list[Any] = []
        # sprite position
        self.pos: pygame.Vector2 = pygame.Vector2()
        # sprite sheet
        self.sprite_sheet: SpriteSheet = SpriteSheet("")
        # sprite type
        self.type: str = type
        # blitting image (could be a sprite sheet)
        self.image: pygame.Surface | None = None
        # rect in which sprite will be drawn/interracted with
        self.rect: pygame.Rect
        # special flags idk yet
        self.special_blit_flags: int
        # in server id for identetification
        self.in_server_id: int
        # try not to use area rect
    def draw(self, screen: pygame.Surface, *args, **kwargs) -> None:
        ...
    def update(self, *args, **kwargs) -> None:
        ...


class Entity(Sprite):
    def __init__(self, name:str="Unamed Entity", speed: int=200, groups: List[pygame.sprite.Group] = [], type: str = "any",
                 isid:int=0,x:int=0,y:int=0,state:int=0,direction:int=0) -> None:
        super().__init__(groups, type)
        self.last_state =  {"x":0, "y":0, "state":IDLE, "direction":RIGHT}
        self.name_surf: pygame.Surface
        self.color: Tuple[int,int,int] = (0,0,255)
        self.name: str = name
        self.in_server_id = 0 if isid == 0 else isid
        self.in_server_id_bytes = b"" # not here
        
        # direction entity is faceing (for animations) not direction it's moving
        self.facing: int = RIGHT
        self.frame_index: int = 0
        self.fps: int = 10
        self.state = IDLE if state == 0 else state

        # speed by which entity moves
        self.speed: float = speed
        self.dash_speed: float = speed * 3.5
        # velocity will be the final direction player will move (calculated by summing all the forces + movement)
        self.velocity: pygame.Vector2 = pygame.Vector2()
        # direction entity is moving (not necessarily faceing)
        self.direction: int = RIGHT if direction == 0 else direction
        self.pos = pygame.Vector2(x,y)

    def __move(self, *args, **kwargs) -> None:
        # for entity to move e.g. AI, keyboard movement, controler...
        ...
    def update(self, *args, **kwargs) -> None:
        """
        # update in serialisation. this is for sending data
        self.last_state["x"] = int(self.pos.x)
        self.last_state["y"] = int(self.pos.y)
        self.last_state["state"] = self.state
        self.last_state["direction"] = self.direction
        """
        return super().update(*args, **kwargs)
    def __repr__(self) -> str:
        return f"Entity \"{self.name}\":{self.in_server_id} at {self.pos.x:3f}:{self.pos.y:3f} direction: {self.direction}"
class SpriteSheet:
    def __init__(self, path: str, sf: float | int = 0) -> None:
        try:
            s =  pygame.image.load(path).convert_alpha()
        except:
            s = pygame.Surface((0,0))
        self.sprite_sheet = pygame.transform.scale(s, (s.get_width() * sf, s.get_height() * sf))
        self.rect: pygame.Rect = self.sprite_sheet.get_rect()
        self.animations: Animation = Animation()
        self._sprite_width: int = 0
        self._sprite_height: int = 0

    @property
    def ss(self) -> pygame.Surface:
        return self.sprite_sheet
    @property
    def sprite_width(self):
        return self._sprite_width

    @sprite_width.setter
    def sprite_width(self, value):
        self._sprite_width = value

    @property
    def sprite_height(self):
        return self._sprite_height


    @sprite_height.setter
    def sprite_height(self, value):
        self._sprite_height = value

    @property
    def sw(self):
        return self.sprite_width

    @property
    def sh(self):
        return self.sprite_height
