import json
from logger import log, err

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

        try:
            with open("./config/config.json") as f:
                js = json.load(f)
        except Exception as e:
            err(f"Failed to read config: {e}")
            return

        app_config = js.get("app", {})
        map_config = js.get("map", {})

        self.a_fullscreen = app_config.get("fullscreen", False)
        self.a_screen_w = app_config.get("screen_width", False)
        self.a_screen_h = app_config.get("screen_height", False)
        self.a_intended_screen_w = app_config.get("canvas_intended_width", False)
        self.a_intended_screen_h = app_config.get("canvas_intended_height", False)
        self.m_tile_width = map_config.get("tile_width", 128)
        self.m_tile_height = map_config.get("tile_height", 128)

        self.initialized = True
        log(f"Initialised config {n_of_config_initialisation}'th time")

