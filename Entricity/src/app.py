from logging import exception
from threading import Thread
from typing import Tuple
import pygame, sys
from time import sleep
from game import Game
from logger import log, err
from context import Config
from connections import Connections
import tkinter as tk
from tkinter import messagebox


class App:
    def __init__(self) -> None:
        self.cfg: Config
        self.__screen: pygame.Surface 
        self.__screen_size: Tuple[int, int]
        self.__screen_flags: int = 0
        self.__clock: pygame.time.Clock 
        self.conn: Connections

        # Errors
        self.app_error: Exception | None = None
        self.menu_error_text: pygame.Surface
        self.menu_error_rect: pygame.Rect

        try:
            pygame.init()
            pygame.display.set_caption("Entricity")
            self.cfg = Config()
            self.__screen_size = (self.cfg.a_screen_w, self.cfg.a_screen_h)
            if self.cfg.a_fullscreen: self.__screen_flags += pygame.FULLSCREEN
        except Exception as e:
            err(f"Got an exception in creating app info: {e}. Fatal. Exiting...")
            return
        self.__screen: pygame.Surface = pygame.display.set_mode(
                self.__screen_size,
                self.__screen_flags | pygame.DOUBLEBUF
            )
            
        self.__clock = pygame.time.Clock()

        self.__load()
        self.__run()
        self.__cleanup()

    def update_loading_message(self, msg:str) -> None:
        self.loading_message = msg
        self.loading_text = self.cfg.font.render(self.loading_message, True, (255,255,255))
        self.loading_rect = self.loading_text.get_rect(center=(self.__screen_size[0] // 2, self.__screen_size[1] // 2))

    def __load(self) -> None:
        self.loading_state = "loading"
        self.loading_message = ""
        self.loading_text = self.cfg.font.render(self.loading_message, True, (255,255,255))
        self.loading_rect = self.loading_text.get_rect(center=self.__screen_size)

        def __create(self) -> None:
            self.loading_message = "Setting things up"
            sleep(1)
            self.loading_message = "Creating connection to server..."
            log("Trying connection")
            try:
                self.conn = Connections()
            except Exception as e:
                err(f"Failed to create connection to server: {e}. Fatal. Extiting...")
                self.app_error = e
                self.loading_state = "fatal"
                return
            self.loading_message = "Done!"
            sleep(1)
            self.loading_state = "done"
            log("done connecting")

        th = Thread(target=__create, args=[self,])
        th.daemon = True
        th.name = "app loading thread"
        th.start()
        pt = ""
        while self.loading_state != "done":
            if self.loading_message != pt:
                self.update_loading_message(self.loading_message)
            if self.loading_state == "fatal":
                self.__fatal_error_warning()
                raise Exception("Fatal error occured.")
            
            self.__screen.fill((0,0,0))
            self.__screen.blit(self.loading_text, self.loading_rect)
            pygame.display.flip()
            ...

    def set_app_error(self, e: Exception) -> None:
        self.app_error = e
        str_err: str
        try:
            str_err = str(self.app_error)[:50] + "..."
        except:
            str_err = str(self.app_error)
        self.menu_error_text = self.cfg.sfont.render(str_err, True, (255, 0, 0))
        self.menu_error_rect = self.menu_error_text.get_rect(center=(
            self.__screen_size[0] // 2,
            self.__screen_size[1] // 2
            ))

    def __fatal_error_warning(self):
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        e: str
        try:
            e = str(self.app_error)[:50] + "..."
        except:
            e = str(self.app_error)

        messagebox.showinfo("Fatal Error", f"An error occured:\n{e}\nCheck log file for more information.")
        root.destroy()
        self.__cleanup()
        sys.exit(-1)
        
    
    def __run_game(self) -> int:
        log("Running game...")
        try:
            g = Game()
            g.set_conn(self.conn)
            return g.run()
        except Exception as e:
            self.app_error = e

        log("Finished running game")
        return 0

    def __run(self) -> None:
        log("in main app loop")
        EntricityText = self.cfg.lfont.render("Entricity", True, 0xffffff)
        EntricityTextRect = EntricityText.get_rect(center=(
                self.__screen_size[0] //2,
                self.__screen_size[1] //2
                ))

        gText = self.cfg.sfont.render("press \"G\" to start game", True, 0xffffff)
        gRect = gText.get_rect(center=(
            self.__screen_size[0] // 2,
            self.__screen_size[1] // 2 + 70
            ))


        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return
                if e.type == pygame.KEYUP:
                    if e.key == pygame.K_g:
                        if self.__run_game() == -1:
                            return
                    elif e.key == pygame.K_q:
                        return

            self.__screen.fill(0x000)
            self.__screen.blit(EntricityText, EntricityTextRect)
            self.__screen.blit(gText, gRect)
            if self.app_error:
                self.__screen.blit(
                    self.menu_error_text,
                    self.menu_error_rect
                                   )
            pygame.display.update()
            self.__clock.tick(60)

    def __cleanup(self) -> None:
        log("Cleaning up App...")
        ...

