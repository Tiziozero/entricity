import pygame, sys, json
import tkinter as tk
from tkinter import messagebox

from logger import log, warn, err
from connections import Connections

n_of_config_initialisation = 0

class Config:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance == None:
            cls._instance = super(Config, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    
    def __init__(self) -> None:
        if hasattr(self, 'initialized') and self.initialized:
            return

        if not pygame.get_init():
            pygame.init()

        self.screen: pygame.Surface
        self.conn: Connections | None = None

        self.lfont  = pygame.font.Font("./assets/fonts/CascadiaCode/CaskaydiaCoveNerdFont-Regular.ttf", 70)
        self.font   = pygame.font.Font("./assets/fonts/CascadiaCode/CaskaydiaCoveNerdFont-Regular.ttf", 35)
        self.sfont  = pygame.font.Font("./assets/fonts/CascadiaCode/CaskaydiaCoveNerdFont-Regular.ttf", 20)
        self.xsfont = pygame.font.Font("./assets/fonts/CascadiaCode/CaskaydiaCoveNerdFont-Regular.ttf", 12)

        try:
            with open("./config/config.json") as f:
                js = json.load(f)
        except Exception as e:
            err(f"Failed to read config: {e}")
            self.fatal_error_warning(str(e))
            raise e

        app_config = js.get("app", {})

        self.a_fullscreen = app_config.get("fullscreen", False)
        self.a_screen_w = app_config.get("screen_width",  1440)
        self.a_screen_h = app_config.get("screen_height", 1080)
        self.canvas_screen_w = app_config.get("canvas_width",  1440)
        self.canvas_screen_h = app_config.get("canvas_height", 1080)
        self.screen = pygame.display.set_mode((self.a_screen_w, self.a_screen_h))

        # screen / canvas
        self.screen_multiplier = self.a_screen_w / self.canvas_screen_w
        self.screen_scale_factor = self.a_screen_w / self.canvas_screen_w
        log(f"Screen multiplier: {self.screen_multiplier}: {self.a_screen_w}, {self.canvas_screen_w}")

        try:
            self.conn = Connections()
        except Exception as e:
            err(f"Could create connections: {e}")
            self.fatal_error_warning(str(e))
            self.conn = None

        self.initialized = True
        log(f"Initialised config {n_of_config_initialisation}'th time")

    def fatal_error_warning(self, error: str):
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        messagebox.showinfo("Fatal Error", f"An error occured:\n{error}\nCheck log file for more information.")
        root.destroy()
        sys.exit(-1)
    def light_error_warning(self, error: str):
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        messagebox.showinfo("Error", f"An error occured:\n{error}\nCheck log file for more information.")
        root.destroy()

