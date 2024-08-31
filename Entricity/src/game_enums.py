from enum import Enum

class EntityStates(Enum):
    IDLE        = 1
    WALKING     = 2
    ATTACKING   = 3

class EntityDirections(Enum):
    LEFT        = 1
    RIGHT       = 2
    UP          = 3
    DOWN        = 4
