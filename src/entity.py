import pygame

class Entity(pygame.sprite.Sprite):
    def __init__(self, *groups: pygame.sprite.Group) -> None:
        super().__init__(*groups)
        self.type: str
        self.image: pygame.surface.Surface = pygame.surface.Surface((0,0))
        self.rect = self.image.get_rect()
