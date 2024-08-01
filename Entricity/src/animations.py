import json
from typing import Dict
from constants import *

class AnimationInfo:
    def __init__(self, l: int, c: int):
        # length
        self.l: int = l
        # col
        self.c: int = c

    def __repr__(self) -> str:
        return f"AnimationInfo l:{self.l};r:{self.c}"

## to update with directions
class Animations:
    def __init__(self, config_path:str) -> None:
        self.config_path = config_path
        self.animations: Dict[int, AnimationInfo] = {}
        ## animation info
        # updated using dt
        self.frame_update_index: float = 0.0
        # acctual frame index
        self.frame_index: int = 0
        self.fps: int
        self.facing: int = RIGHT
        self.__load_animations()

    def __load_animations(self) -> None:
        with open(self.config_path, "r") as f:
            js = json.loads(f.read())
            if js.get(CONFIG_TYPE, None) != ANIMATIONS_CONFIG:
                raise ValueError("Animations Config type isn't of type animations config type")
            data = js.get(CONFIG_DATA, None)
            if data == None or data == {}:
                raise ValueError("Animations Config Data is empty/missing/invalid")

            fps = data.get(ANIMATIONS_FPS, None)
            if fps == None or fps < 0:
                raise ValueError("Animations Config fps is empty/missing/invalid")
            self.fps = fps

            animations = data.get(ANIMATIONS_ANIMATIONS, None)
            if animations == None or animations == []:
                raise ValueError("Animations Config animations empty/missing/invalid")

            # animations
            ## Eventually add more states and animations
            animation  = animations.get(ANIMATIONS_IDLE, None)
            if animation == None:
                raise ValueError("Couldn't find ANIMATIONS_IDLE")
            l = animation.get(ANIMATIONS_INFO_LENGTH, -1)
            c = animation.get(ANIMATIONS_INFO_ROW, -1)
            if l == -1 or c == -1:
                raise ValueError("Couldn't find ANIMATIONS_IDLE information")
            ai = AnimationInfo(l,c)
            self.animations[ANIMATION_IDLE] = ai

            animation  = animations.get(ANIMATIONS_WALK, None)
            if animation == None:
                raise ValueError("Couldn't find ANIMATIONS_WALK")
            l = animation.get(ANIMATIONS_INFO_LENGTH, -1)
            c = animation.get(ANIMATIONS_INFO_ROW, -1)
            if l == -1 or c == -1:
                raise ValueError("Couldn't find ANIMATIONS_WALK information")
            ai = AnimationInfo(l,c)
            self.animations[ANIMATION_WALKING] = ai
             
            ## Handle attacks differently
            """
            animation  = animations.get(ANIMATIONS_BASE_ATTACK, None)
            if animation == None:
                raise ValueError("Couldn't find ANIMATIONS_BASE_ATTACK")
            # row column
            ai = AnimationInfo(
                animation.get(ANIMATIONS_INFO_LENGTH),
                animation.get(ANIMATIONS_INFO_ROW))
            self.animations[ANIMATION_BASE_ATTACK] = ai
            """
        ...

