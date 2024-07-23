from enum import Enum
from typing import final
from logger import *
import pygame, sys
from time import sleep


from threading import Thread

from connections import Connections

class SceneLoadingState(Enum):
    STATE_DONE = "done"
    STATE_ERROR = "error"
    STATE_LOADING = "loading"

class Scene:
    def __init__(self) -> None:
        self.screen: pygame.Surface = pygame.display.get_surface()

    def load(self) -> None:
        ...

    def draw(self) -> None:
        ...

    def loop(self):
        ...
