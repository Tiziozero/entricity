from constants import *

class AnimationInfo:
    def __init__(self) -> None:
        self.l: int = 0
        self.r: int = 0

    def init(self, l: int, r: int):
        self.l = l
        self.r = r

class Animation:
    def __init__(self) -> None:
        self.idle:              AnimationInfo = AnimationInfo()
        self.walk:              AnimationInfo = AnimationInfo()
        self.base_attack:       AnimationInfo = AnimationInfo()
        self.special_attack:    AnimationInfo = AnimationInfo()
        
        ## animation info
        self.animation_index: float = 0.0
        self.fps: int = 10
        self.facing: int = RIGHT
    def  __getitem__(self, v):
        if v == IDLE:
            return self.idle
        if v == WALKING:
            return self.walk
        if v == ATTACKING:
            return self.base_attack
