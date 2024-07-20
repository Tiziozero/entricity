from typing import List, Optional
from enum import Enum
import pygame

import uuid

def generate_unique_id(prefix: str) -> str:
    """
    Generates a unique ID with the format 'e<three_letters>-<unique_part>'.
    
    Parameters:
    prefix (str): A three-letter prefix.
    
    Returns:
    str: A unique ID string.

    """
    if len(prefix) != 3 or not prefix.isalpha():
        raise ValueError("Prefix must be exactly three letters.")
    

    unique_part = uuid.uuid4().hex  # Generate a unique identifier
    return f"e{prefix}-{unique_part}"

class XYWHAttribute:
    def __init__(self,
                 top:int=0,
                 bottom:int=0,
                 left:int=0,
                 right:int=0,
                 x:int=0,
                 y:int=0
                 ) -> None:
        # define
        self._top: int
        self._bottom: int
        self._left: int
        self._right: int
        # initialise
        self._top = y
        self._bottom = y
        self._left: int = x
        self._right: int = x
        if top:
            self._top: int = top
        if bottom:
            self._bottom: int = bottom
        if left:
            self._left: int = left
        if right:
            self._right: int = right

    def __repr__(self) -> str:
        return f"{self.top}:{self.bottom}:{self.left}:{self.right}"

    @property
    def top(self) -> int:
        return self._top

    @top.setter
    def top(self, value: int) -> None:
        self._top = value

    @property
    def bottom(self) -> int:
        return self._bottom

    @bottom.setter
    def bottom(self, value: int) -> None:
        self._bottom = value

    @property
    def right(self) -> int:
        return self._right

    @right.setter
    def right(self, value: int) -> None:
        self._right = value

    @property
    def left(self) -> int:
        return self._left

    @left.setter
    def left(self, value: int) -> None:
        self._left = value

    @property
    def x(self) -> int:
        return self._left + self._right

    @x.setter
    def x(self, value: int) -> None:
        self._left = value
        self._right = value

    @property
    def y(self) -> int:
        return self._top + self._bottom

    @y.setter
    def y(self, value: int) -> None:
        self._top = value
        self._bottom = value


class Margin(XYWHAttribute):
    def __init__(self, top: int = 0, bottom: int = 0, left: int = 0, right: int = 0, x: int = 0, y: int = 0) -> None:
        super().__init__(top, bottom, left, right, x, y)
class Padding(XYWHAttribute):
    def __init__(self, top: int = 0, bottom: int = 0, left: int = 0, right: int = 0, x: int = 0, y: int = 0) -> None:
        super().__init__(top, bottom, left, right, x, y)
class Border(XYWHAttribute):
    def __init__(self, border_width:int=0, top: int = 0, bottom: int = 0, left: int = 0, right: int = 0, x: int = 0, y: int = 0, radius:int=0) -> None:
        super().__init__(top, bottom, left, right, x, y)
        self.border_width: int = border_width
        self.border_radius: int = radius

class Display(Enum):
    INLINE = "inline"
    FLEX = "flex"
    BLOCK = "block"

class Element:
    def __init__(self, parent: Optional['Element'] = None, name:str="lem") -> None:
        self.parent: Optional['Element'] = parent
        self.surface: pygame.Surface = pygame.Surface((0,0))
        self.margin: Margin = Margin()
        self.padding: Padding = Padding()
        self.display: Display = Display.BLOCK
        self.width = -1
        self.height = -1
        self.m_width = -1
        self.m_height = -1
        self.border: Border = Border(0)
        self.border_radius:int=-1
        self.elements: List[Element]

        
        self.id=generate_unique_id(name)
        self.name = self.id


        """
            Body of the element. This determinates the minimum width
            and height of the element.
        """
        self.bodyr: pygame.Rect = self.surface.get_rect()
        """
            Rect that includes padding and body rect.
            Each side is calculated with:
                self.bodyr.<side>   +
                self.padding.<side>
        """
        self.paddingr: pygame.Rect = pygame.Rect(0,0,0,0)
        """
            Border of the element
            This will be hollow so when blitting:
                (function) def rect(
                    surface: Surface,
                    color: ColorValue,
                    rect: RectValue,
                    width: int = 0,
                    border_radius: int = -1,
                    border_top_left_radius: int = -1,
                    border_top_right_radius: int = -1,
                    border_bottom_left_radius: int = -1,
                    border_bottom_right_radius: int = -1
                ) -> Rect
            rect can be set as "Element.borderr".
            "border-radius" can be set here too.

            Each side is calculated with:
                self.bodyr.<side>   +
                self.padding.<side> +
                self.border.<side>
        """
        self.borderr: pygame.Rect = pygame.Rect(0,0,0,0)
        """
            Rect that includes margin, border, padding and body rect.
            This will decide position and final dimensions of the rect
            Each side is calculated with:
                self.bodyr.<side>   +
                self.padding.<side> +
                self.border.<side>  +
                self.margin.<side>  
        """
        self.marginr: pygame.Rect = pygame.Rect(0,0,0,0)

        self.blit_area_rect = self.surface.get_rect()

        self.z_index: int = 0
        self.screen_size = pygame.display.get_surface().get_size()
    def print(self):
        if hasattr(self, "elements"):
            print(";".join([e.id for e in self.elements]))

    def upadate_dimentions(self) -> None:
        self.blit_area_rect.w = self.bodyr.w
        self.blit_area_rect.h = self.bodyr.h
        if self.width > 0:
            self.bodyr.w = self.width
            self.blit_area_rect.w = self.width
        if self.height > 0:
            self.bodyr.h = self.height
            self.blit_area_rect.h = self.height
        self.paddingr.w = self.bodyr.w + self.padding.x
        self.paddingr.h = self.bodyr.h + self.padding.y

        self.borderr.w = self.paddingr.w + self.border.x
        self.borderr.h = self.paddingr.h + self.border.y

        self.marginr.w = self.borderr.w + self.margin.x
        self.marginr.h = self.borderr.h + self.margin.y
        print(f"{self.name}: width: {self.marginr.w}, height: {self.marginr.h}")

    def update_on_margin_rect(self) -> None:
        self.borderr.x = self.marginr.x + self.margin.left
        self.borderr.y = self.marginr.y + self.margin.top
        # setting padding rect
        self.paddingr.x = self.borderr.x + self.border.left
        self.paddingr.y = self.borderr.y + self.border.top
        # setting body rect
        self.bodyr.x = self.paddingr.x + self.padding.left
        self.bodyr.y = self.paddingr.y + self.padding.top

    def define_structure(self, startx: int, starty: int):
        self.define_totalrect()
        self.marginr.x = (startx)
        self.marginr.y = (starty)
        
        self.update_on_margin_rect()

        estartx = self.bodyr.x
        estarty = self.bodyr.y
        pesy = estarty
        if hasattr(self, "elements"):
            for e in self.elements:
                # assuming divs go down like columns
                e.define_structure(estartx, estarty)
                estartx += 0 # e.srect.w
                estarty += e.marginr.h
                pesy = estarty

    def define_totalrect(self) -> None:
        self.upadate_dimentions()
    def draw(self, surface: pygame.Surface):
        ...
