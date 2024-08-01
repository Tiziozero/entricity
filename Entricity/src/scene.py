from time import sleep
from typing import Any, Callable, List, TypeVar
from logger import *
import pygame, sys

from threading import Thread

from connections import Connections
from constants import *
from context import Config


class Scene:
    def __init__(self) -> None:
        self.screen: pygame.Surface = pygame.display.get_surface()
        self._cfg: Config = Config()
        self._clock: pygame.time.Clock = pygame.time.Clock()
        self.ui: List[Any] = []
        self.on: bool = True

        self._scene_loading_state: str = LOADING_STATE_PENDING
        self._scene_loading_screen: pygame.Surface = pygame.Surface(self.screen.get_size())
        self._scene_loading_screen.fill((0,0,0))
        self.__default_loading_screen_image: pygame.Surface = pygame.image.load(
            "./assets/loading_screen.jpg"
        ).convert_alpha()
        s = self.__default_loading_screen_image.get_size()
        log(f"{(s[0] * Config().screen_multiplier, s[1] * Config().screen_multiplier)}")
        self.__default_loading_screen_image = pygame.transform.scale(
        self.__default_loading_screen_image, (s[0] * Config().screen_multiplier, s[1] * Config().screen_multiplier)
        )
        self.__default_loading_screen_rect = self.__default_loading_screen_image.get_rect()
        self.__loading_progress: float = 0.0


    def default_loading_screen(self):
        self.screen.blit(self.__default_loading_screen_image, self.__default_loading_screen_rect)
        ...

    # loader returns either a loading state or nothing
    def load(self, loader: Callable[[Any], str|None], screen) -> None:
        def __loader(scene):
            ls = loader(scene)
            if not ls or ls == LOADING_STATE_DONE:
                self._scene_loading_state = LOADING_STATE_DONE
            else:
                self._scene_loading_state = ls

        if screen == None:
            screen = self.default_loading_screen

        self._scene_loading_state = LOADING_STATE_LOADING
        th = Thread(target=__loader, args=[self,])
        th.daemon = True
        th.name = "scene loader thread"
        th.start()
        log("Stated loader thread")
        screen_size = pygame.display.get_surface().get_size()
        display_rect = pygame.Rect(0, screen_size[1] - 5, 0, 5)
        while self._scene_loading_state == LOADING_STATE_LOADING:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self._scene_loading_state = LOADING_STATE_ERROR
            # Draw loading screen
            screen()

            # Draw progress bar
            display_rect.w = int(screen_size[0] * self.__loading_progress)
            pygame.draw.rect(
                self.screen,
                (255,255,255),
                display_rect
            )
                
            pygame.display.flip()
        
    """
        Handles quit and ui events
    """
    def update(self) -> List[pygame.event.Event]:
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                self.on = False
                return []
            for e in self.ui:
                e.hanle_event(e)
        return events

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill("black")
        for e in self.ui:
            e.draw(screen)
        pygame.display.flip()
        ...

    def start(self):
        self.load(lambda _: print("Loading scene function"), lambda _: print("Loading screen"))
        while self.on:
            self.update()
            self.draw(self.screen)
