import pygame
from game import Game
from logger import log
from context import Config
class App:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Entricity")
        self.cfg: Config = Config()

        self.__screen: pygame.Surface 
        self.__screen_size = (self.cfg.a_screen_w, self.cfg.a_screen_h)
        self.__screen_flags = 0
        self.app_error = None

        self.font = pygame.font.Font("./assets/fonts/CascadiaCode/CaskaydiaCoveNerdFont-Regular.ttf", 30)

        if self.cfg.a_fullscreen: self.__screen_flags += pygame.FULLSCREEN
        self.__screen: pygame.Surface = pygame.display.set_mode(
                self.__screen_size,
                self.__screen_flags | pygame.DOUBLEBUF
            )

        self.__clock: pygame.time.Clock = pygame.time.Clock()

        self.__run()
    
    def __run_game(self) -> int:
        log("Running game...")
        try:
            g = Game()
            g.run()
        except Exception as e:
            self.app_error = e

        log("Finished running game")
        return 0

    def __run(self) -> None:
        log("in main app loop")
        msg = "Entricity"
        EntricityText = self.font.render("Entricity", True, 0xffffff)
        gText = self.font.render("press \"G\" to start game", True, 0xfff)
        size = gText.get_size()
        gText = pygame.transform.scale(gText, (size[0]//3, size[1]//3))
        gRect = gText.get_rect()
        e = None
        s_size = EntricityText.get_size()
        r = pygame.Rect(
                self.__screen_size[0] //2 - s_size[0] // 2,
                self.__screen_size[1] //2 - s_size[1] // 2,
                s_size[0],
                s_size[1]
                )
        if self.app_error:
            e = str(self.app_error)
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return
                if e.type == pygame.KEYUP:
                    if e.key == pygame.K_g:
                        self.__run_game()
                    elif e.key == pygame.K_q:
                        return

            self.__screen.fill(0x000)
            self.__screen.blit(EntricityText, r)
            self.__screen.blit(gText, gRect)
            pygame.display.update()
            self.__clock.tick(60)


