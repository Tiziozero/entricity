import pygame
from game import Game
from logger import log
from context import Config
class App:
    def __init__(self) -> None:
        pygame.init()
        log("Pygame set up")
        self.cfg: Config = Config()
        self.__screen_size = (self.cfg.a_screen_w, self.cfg.a_screen_h)
        self.__screen_flags = 0
        if self.cfg.a_fullscreen: self.__screen_flags += pygame.FULLSCREEN
        self.__screen: pygame.Surface = pygame.display.set_mode(
                self.__screen_size,
                self.__screen_flags | pygame.DOUBLEBUF
            )
        pygame.display.set_caption("Entricity")

        self.__clock: pygame.time.Clock = pygame.time.Clock()
        self.__run()
    
    def __run_game(self) -> int:
        log("Running game...")
        g = Game()
        g.run()
        log("Finished running game")
        return 0

    def __run(self) -> None:
        log("in main app loop")
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return
                if e.type == pygame.KEYUP:
                    if e.key == pygame.K_g:
                        self.__run_game()
                    elif e.key == pygame.K_q:
                        return

            self.__screen.fill("purple")
            pygame.display.update()
            self.__clock.tick(60)


