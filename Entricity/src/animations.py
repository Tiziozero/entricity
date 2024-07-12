class AnimationInfo:
    def __init__(self) -> None:
        self.l: int
        self.r: int

    def init(self, l: int, r: int):
        self.l = l
        self.r = r

class Animation:
    def __init__(self) -> None:
        self.idle:              AnimationInfo = AnimationInfo()
        self.walk:              AnimationInfo = AnimationInfo()
        self.base_attack:       AnimationInfo = AnimationInfo()
        self.special_attack:    AnimationInfo = AnimationInfo()
