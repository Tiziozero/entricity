import pygame
from typing import List

from animations import Animation
from game_enums import EntityStates, EntityDirections

class Sprite(pygame.sprite.Sprite):
    def __init__(self, groups: List[pygame.sprite.Group]=[], type:str ="any") -> None:
        super().__init__(*groups)
        # sprite sheet
        self.sprite_sheet: SpriteSheet = SpriteSheet("./assets/characters/char1/char1_idle.png")
        # sprite type
        self.type: str = type
        # blitting image (could be a sprite sheet)
        self.image: pygame.Surface | None = pygame.Surface((0,0))
        # rect in which sprite will be drawn/interracted with
        self.rect: pygame.Rect = self.image.get_rect()
        # area of image (sprite sheet which will be drawn)
        self.area_rect: pygame.Rect = self.image.get_rect()
        # special flags idk yet
        self.special_blit_flags: int = 0

class Entity(Sprite):
    def __init__(self, name:str="Unamed Entity", speed: int=200, groups: List[pygame.sprite.Group] = [], type: str = "any") -> None:
        super().__init__(groups, type)
        self.name: str = name
        
        # direction entity is faceing (for animations) not direction it's moving
        self.facing: EntityDirections = EntityDirections.RIGHT
        self.frame_index: int = 0
        self.fps: int = 10
        self.state = EntityStates.IDLE

        # entity position
        self.pos: pygame.Vector2 = pygame.Vector2()
        # speed by which entity moves
        self.speed: float = speed
        self.dash_speed: float = speed * 3.5
        # velocity will be the final direction player will move (calculated by summing all the forces + movement)
        self.velocity: pygame.Vector2 = pygame.Vector2()
        # direction entity is moving (not necessarily faceing)
        self.direction: str = "right"

    def __move(self, *args, **kwargs) -> None:
        # for entity to move e.g. AI, keyboard movement, controler...
        ...
class SpriteSheet:
    def __init__(self, path: str, sf: float | int = 0) -> None:
        s =  pygame.image.load(path).convert_alpha()
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
