from threading import Thread
from enum import Enum
from typing import Any, List, Tuple
import pygame, sys
from time import sleep
from game import Game
from logger import log, err
from context import Config
from connections import Connections
import tkinter as tk
from tkinter import messagebox
class Event(Enum):
    EVENTGAME = "game"
    EVENTSETTINGS = "settings"

class Element:
    def __init__(self) -> None:
        self.rect: pygame.Rect = pygame.Rect(0,0,0,0)
        self.image: pygame.Surface = pygame.Surface((0,0))
        ...
    def update(self, dt: float) -> None:
        ...
    def on_hover(self) -> None:
        ...
    def on_click(self, *args, **kwargs) -> Any:
        ...
    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, self.rect)

class Button(Element):
    def __init__(self, txt:str, center: Tuple[int,int] = (0,0)) -> None:
        self.image: pygame.Surface = pygame.image.load("assets/ui elements/base button flat.png").convert_alpha()
        self.image_size = self.image.get_size()
        ## in future divide image size by some multiplier
        self.image = pygame.transform.scale(self.image, (self.image_size[0] // 10, self.image_size[1] // 10))
        self.image_size = self.image.get_size()
        self.txt = Config().sfont.render(txt, True, (255,255,255))
        self.trect = self.txt.get_rect(center=(self.image_size[0] // 2, self.image_size[1] // 2))
        self.image.blit(self.txt, self.trect)
        self.rect = self.image.get_rect(center=center)
        self.event = Event.EVENTGAME

    def on_click(self, *args, **kwargs) -> Event:
        log("Button Clieckd")
        return self.event
    def update(self, dt: float) -> None:
        return super().update(dt)
    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, self.rect)
        


