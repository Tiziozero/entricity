import json
import pygame
from typing import List, Any
from constants import *

from logger import log, warn, err
from animations import AnimationInfo, Animations
from context import Config

# What of the entity can change
class State:
    def __init__(self,
            p: pygame.Vector2 = pygame.Vector2(),
            v: pygame.Vector2 = pygame.Vector2(),
            s: int = STATE_IDLE,
            d: int = RIGHT,
            h: int = 0
        ) -> None:
        self.pos: pygame.Vector2 = p
        self.velocity: pygame.Vector2 = v
        self.state: int = s
        self.direction: int = d
        self.health: int = h
    def copy(self):
        return State(self.pos.copy() , self.velocity.copy(), self.state, self.direction, self.health)

    def __repr__(self) -> str:
        return f"{self.pos}:{self.velocity}:{self.state}:{self.direction}"

class Sprite:
    def __init__(self, groups: List[pygame.sprite.Group]=[], type:str ="any") -> None:
        super().__init__(*groups)
        self.in_server_id: int
        self.sprite_type = type

        self.state = State()
        self.last_state = State()

        # SpriteGroup but import cycle so... ye
        self.groups: list[Any] = []
        # sprite position
        self.pos: pygame.Vector2 = pygame.Vector2()
        self.rect: pygame.Rect = pygame.Rect(0,0,0,0)

        # animations
        # sprite type
        self.sprite_sheet: SpriteSheet
        # try not to use area rect

    # top left
    def get_pos(self) -> pygame.Vector2:
        return self.pos.copy()
    def draw(self, *args, **kwargs) -> None:
        ...

    def update(self, *args, **kwargs) -> None:
        ...

class Entity(Sprite):
    def __init__(self,
        groups: List[pygame.sprite.Group] = [], type: str = "entity",
        entity_id: str="",
        ) -> None:
        super().__init__(groups, type)

        self.entity_id = entity_id
        # Entity Name: eg Wizart
        self.name: str


        # determinates weather the entity can attack
        # Should be set True by attack cooldown timer
        self.can_attack: bool = True

        # Will be set if entity is attacking
        # Extends beyond attack time
        # Can be true even if can attack is true
        # while attacking, state is set to attacking
        self.attacking: bool = False

        # speed by which entity moves
        self.speed: float = 0
        # Speed of entity when running
        self.dash_speed: float = self.speed * 3.5

        self.__load_entity()

    def __load_entity(self) -> None:
        path = "assets/characters/Soldier/config.json"
        path = "assets/characters/Wizart/config.json"
        path = "assets/characters/entriciboi/config.json"
        try:
            with open(path, "r") as f:
                data = f.read()
                js = json.loads(data)
                # print(data, js)
        except Exception as e:
            err(f"{e} in loading Entity: {self.entity_id}")
            raise e

        type = js.get(CONFIG_TYPE, None)
        if type == None:
            raise ValueError(f"Missing entity type in entity: {self.entity_id}")
        if type != TYPE_ENTITY:
            raise ValueError(f"Invalid/wrong type for entity: {self.entity_id}")

        data = js.get(CONFIG_DATA, None)    
        if data == None:
            raise ValueError(f"Missing entity data in entity: {self.entity_id}")

        self.name = data.get(ENTITY_CONFIG_NAME, None)
        if self.name == None or self.name == "":
            raise ValueError("Entity name not found/empty/invalid")

        log(f"Loading {self.name}...")
        self.entity_id = data.get(ENTITY_CONFIG_ENTITY_ID, None)
        if self.entity_id == None or self.entity_id == "":
            raise ValueError("Entity entity_id not found/empty/invalid")

        self.speed = data.get(ENTITY_CONFIG_SPEED, None)
        if self.speed == None:
            raise ValueError("Entity Speed not found/invalid")
        self.dash_speed: float = self.speed * 3.5


        sprite_sheet_path = data.get(SPRITE_SHEET_CONFIG, None)
        if sprite_sheet_path == None or sprite_sheet_path == "":
            raise ValueError("Entity SpriteSheet not found/invalid")

        self.sprite_sheet = SpriteSheet(sprite_sheet_path)
        # Handle Animations too
        animations_path = data.get(ANIMATIONS_PATH, None)
        if animations_path == None or animations_path == "":
            raise ValueError("Entity Animations not found/empty/invalid")
        self.sprite_sheet.animations = Animations(animations_path)


    def move(self, *args, **kwargs) -> None:
        # determinates self.velocity
        # for entity to move e.g. AI, keyboard movement, controler...
        ...

    def update(self, dt: float, *args, **kwargs) -> None:
        # Saves state
        self.last_state = self.state
        # copies last State
        self.state = self.state.copy()
        self.state.velocity = pygame.Vector2() # for update thingy
        # Updates new State

        # moves -> wierd stuff with online ones
        self.move(dt, *args, **kwargs)

        # Handle animation frame updates
        self.sprite_sheet.animations.frame_update_index += self.sprite_sheet.animations.fps * dt
        self.sprite_sheet.animations.frame_index = int(self.sprite_sheet.animations.frame_update_index)

        # Determine facing direction based on velocity
        if self.state.velocity.y > 0:     self.sprite_sheet.animations.facing = DOWN
        elif self.state.velocity.y < 0:   self.sprite_sheet.animations.facing = UP
        if self.state.velocity.x > 0:     self.sprite_sheet.animations.facing = RIGHT
        elif self.state.velocity.x < 0:   self.sprite_sheet.animations.facing = LEFT

        state_flags = 0
        # Set the state based on velocity
        if self.state.velocity.x != 0 or self.state.velocity.y != 0:
            state_flags |= STATE_FLAG_MOVING

        if self.attacking:
            state_flags |= STATE_FLAG_ATTACKING

        # Update position
        self.state.pos += self.state.velocity * dt
        self.rect.topleft = (int(self.state.pos.x), int(self.state.pos.y))

        # Reset velocity for the next frame

        # Update the image and rect size based on the current state and direction
        self.image = self.sprite_sheet.get_frame_to_draw(state_flags, 0)
        self.rect.size = self.image.get_size()

    # Should not be really using this
    def draw(self, screen: pygame.Surface, *args, **kwargs) -> None:
        # screen.blit(self.sprite_sheet.image, self.rect)
        ...



class SpriteSheet:
    def __init__(self, config_path: str) -> None:
        self.image = pygame.Surface((100,100))
        self.image.fill((0,0,0))
        self.config_path: str = config_path
        self.sprite_sheet: pygame.Surface
        self.sprite_scheet_rect: pygame.Rect
        self.sprite_sheet_rows: int
        self.sprite_sheet_columns: int
        self.sprite_sheet_cell_width: int
        self.sprite_sheet_cell_height: int
        self.animations: Animations
        self.load_sprite_sheet()

    def get_frame_to_draw(self, state_flags: int, direction: int) -> pygame.Surface:
        direction = self.animations.facing
        ai: AnimationInfo|None = None
        if state_flags & STATE_FLAG_MOVING:
            ai = self.animations.animations.get(ANIMATION_WALKING, None)
        else:
            ai = self.animations.animations.get(ANIMATION_IDLE, None)

        if ai == None: raise ValueError(f"Missing Animation info for ANIMATION_WALKING")
        if self.animations.frame_update_index >= ai.l: self.animations.frame_update_index = 0.0
        if self.animations.frame_index >= ai.l: self.animations.frame_index = 0
        x = self.animations.frame_index * self.sprite_sheet_cell_width
        y = ai.r * self.sprite_sheet_cell_height
        try:
            self.image = self.sprite_sheet.subsurface(
                (x, y), (self.sprite_sheet_cell_width, self.sprite_sheet_cell_height)
            )

            if direction == UP or direction == LEFT:
                # Draw to the left // invert
                self.image = pygame.transform.flip(self.image, True, False)
            else:
                # draw to the right
                ...
        except Exception as e:
            print("animation index", self.animations.frame_index, self.animations.frame_update_index)
            print(x + self.sprite_sheet_cell_width)
            print(y + self.sprite_sheet_cell_height)
            print(ai.l)
            print(ai.r)
        return self.image

    def load_sprite_sheet(self) -> None:
        try:
            with open(self.config_path, "r") as f:
                data = f.read()
                js = json.loads(data)
                # print(data, js)
                type = js.get(CONFIG_TYPE, None)
                if type != SPRITE_SHEET_CONFIG:
                    raise ValueError("Invalid Sprite sheet config type/Sprite sheet config type is empty")
                data = js.get(CONFIG_DATA, None)
                if data == None:
                    raise ValueError("Sprite Sheet Config data is empty")

                # Should throw and error if it fails
                path = data.get(SPRITE_SHEET_PATH, None)
                # log(path)
                self.sprite_sheet = pygame.image.load(path).convert_alpha()
                self.sprite_sheet_rect = self.sprite_sheet.get_rect()
                
                # Check if dimensions match
                sprite_sheet_size = self.sprite_sheet.get_size()
                config_ss_size = data.get(SPRITE_SHEET_WIDTH, 0), data.get(SPRITE_SHEET_HEIGHT, 0)

                if sprite_sheet_size[0] != config_ss_size[0] or sprite_sheet_size[1] != config_ss_size[1]:
                    err(f"Sprite Sheet dimensions don't match config file dimensions:"
                        f"{sprite_sheet_size[0]}:{config_ss_size[0]}, "
                        f"{sprite_sheet_size[1]}:{config_ss_size[1]}"
                        )
                    raise ValueError("Sprite Sheet dimensions don't match config file dimensions")

                rs = data.get(SPRITE_SHEET_ROWS, None)
                if rs == None:
                    raise ValueError("Sprite Sheet rows Missing")
                self.sprite_sheet_rows = rs
                cs = data.get(SPRITE_SHEET_COLUMNS, None)
                if cs == None:
                    raise ValueError("Sprite Sheet columns Missing")
                self.sprite_sheet_columns = cs
                # cell dimensions
                cw = data.get(SPRITE_SHEET_CELL_WIDTH, None)
                if cw == None:
                    raise ValueError("Sprite Sheet cell width Missing")
                self.sprite_sheet_cell_width = cw
                ch = data.get(SPRITE_SHEET_CELL_HEIGHT, None)
                if ch == None:
                    raise ValueError("Sprite Sheet cell height Missing")
                self.sprite_sheet_cell_height = ch
                self.image = pygame.Surface((cw, ch))
                self.image.fill((0,0,0))
                


        except Exception as e:
            err(f"in loading sprite sprite sheet: {e}")
            raise e

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
