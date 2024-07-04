import pygame


class Tile(pygame.sprite.Sprite):
    def __init__(self, *groups: pygame.sprite.Group) -> None:
        super().__init__(*groups)
        self.image = pygame.image.load("")
        self.rect = self.image.get_rect()
        self.type="ground"
