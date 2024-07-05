from player import Player
from animations import Animation
from logger import log
import pygame

from game_enums import EntityDirections, EntityStates
from sprites import SpriteSheet


SCALE_FACTOR = 4
class SoilderSide1(Player):
    def __init__(self) -> None:
        super().__init__()

        self.image = pygame.Surface((100 * SCALE_FACTOR, 100 * SCALE_FACTOR))
        self.rect = self.image.get_rect()
        self.sprite_sheet = SpriteSheet("./assets/characters/char1/sprite_sheet.png", sf=SCALE_FACTOR)
        # must be hardcoded for each entity
        self.sprite_sheet_rows = 7
        self.sprite_sheet_row_width = 100 * SCALE_FACTOR
        self.sprite_sheet_row_height = 100 * SCALE_FACTOR
        self.animations: Animation = Animation()
        self.animations.idle.init(6, 0)
        self.animations.walk.init(8, 1)
        self.animations.base_attack.init(6, 2)
        self.animations.special_attack.init(6, 3)
        self.state = EntityStates.IDLE
        self.animation_speed_in_ms: float = 1 / self.fps
        self.animation_t: float = 0.0
        self.area_rect = pygame.Rect(
                0,
                0,
                self.sprite_sheet_row_width,
                self.sprite_sheet_row_height
                )

    def update(self, dt) -> None:
        super().update(dt)
        log("Updating SoilderSide1")
        self.animation_t += dt
        if self.animation_t > self.animation_speed_in_ms:
            self.animation_t %= self.animation_speed_in_ms
            self.frame_index += 1
        if self.state == EntityStates.IDLE:
            if self.frame_index >= self.animations.idle.l: self.frame_index = 0
            self.area_rect.y = self.animations.idle.r * self.sprite_sheet_row_height
        if self.state == EntityStates.WALKING:
            if self.frame_index >= self.animations.walk.l: self.frame_index = 0
            self.area_rect.y = self.animations.walk.r * self.sprite_sheet_row_height

        self.area_rect.x = self.frame_index * self.sprite_sheet_row_width

        log(f"{(self.area_rect, self.frame_index)}")
        # dirrection (for now)
        if self.facing == EntityDirections.RIGHT:
            self.image = self.sprite_sheet.ss.subsurface(self.area_rect)
        elif self.facing == EntityDirections.LEFT:
            self.image = pygame.transform.flip(
                    self.sprite_sheet.ss.subsurface(self.area_rect),
                    True,
                    False
                    )
        elif self.facing == EntityDirections.UP:
            self.image = self.sprite_sheet.ss.subsurface(self.area_rect)
        elif self.facing == EntityDirections.DOWN:
            self.image = pygame.transform.flip(
                    self.sprite_sheet.ss.subsurface(self.area_rect),
                    True,
                    False
                    )

