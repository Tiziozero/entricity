from parser import parse
from typing import Tuple


class Area:
    def __init__(self, size:Tuple[int, int ], pos:Tuple[int, int ]=(0,0)) -> None:
        self.x = pos[0]
        self.y = pos[1]
        self.w = size[0]
        self.y = size[1]
        pass

class Element:
    def __init__(self) -> None:
        pass
class Div(Element):
    def __init__(self) -> None:
        super().__init__()
class Canvas(Div):
    def __init__(self) -> None:
        super().__init__()

if __name__ == "__main__":
    with open("index.pygui", "r") as f:
        canvas = parse(f.read())
        print(canvas)

        indent = 0
        print(canvas.value)
        print(canvas.children)
