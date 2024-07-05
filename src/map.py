import pygame


class Tile(pygame.sprite.Sprite):
    def __init__(self, *groups: pygame.sprite.Group) -> None:
        super().__init__(*groups)
        # self.image = pygame.image.load("")
        self.image = pygame.Surface((0,0))
        self.rect = self.image.get_rect()
        self.type="ground"
