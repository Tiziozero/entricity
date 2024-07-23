from typing import Dict, List, Optional
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

fonts: Dict = {}

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

class Style:
    def __init__(self) -> None:
        self.margin: Margin = Margin()
        self.padding: Padding = Padding()
        self.display: Display = Display.BLOCK
        self.width = -1
        self.height = -1
        self.m_width = -1
        self.m_height = -1
        self.border: Border = Border(0)
        self.border_radius:int=-1
        
        """
            Body of the element. This determinates the minimum style.width
            and height of the element.
        """
        self.bodyr: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        """
            Rect that includes style.padding and body rect.
            Each side is calculated with:
                self.style.bodyr.<side>   +
                self.style.padding.<side>
        """
        self.paddingr: pygame.Rect = pygame.Rect(0,0,0,0)
        """
            Border of the element
            This will be hollow so when blitting:
                (function) def rect(
                    surface: Surface,
                    color: ColorValue,
                    rect: RectValue,
                    style.width: int = 0,
                    border_radius: int = -1,
                    border_top_left_radius: int = -1,
                    border_top_right_radius: int = -1,
                    border_bottom_left_radius: int = -1,
                    border_bottom_right_radius: int = -1
                ) -> Rect
            rect can be set as "Element.style.borderr".
            "style.border-radius" can be set here too.

            Each side is calculated with:
                self.style.bodyr.<side>   +
                self.style.padding.<side> +
                self.style.border.<side>
        """
        self.borderr: pygame.Rect = pygame.Rect(0,0,0,0)
        """
            Rect that includes style.margin, style.border, style.padding and body rect.
            This will decide position and final dimensions of the rect
            Each side is calculated with:
                self.style.bodyr.<side>   +
                self.style.padding.<side> +
                self.style.border.<side>  +
                self.style.margin.<side>  
        """
        self.marginr: pygame.Rect = pygame.Rect(0,0,0,0)

        self.z_index: int = 0

class Element:
    def __init__(self, parent: Optional['Element'] = None, name:str="lem") -> None:
        self.parent: Optional['Element'] = parent
        self.style: Style = Style()
        self.elements: List[Element]

        self.element_id=generate_unique_id(name)
        self.name = self.element_id

        self.surface: pygame.Surface = pygame.Surface((0,0))
        self.blit_area_rect = self.surface.get_rect()

        self.screen_size = pygame.display.get_surface().get_size()

    def print(self):
        if hasattr(self, "elements"):
            print(";".join([e.element_id for e in self.elements]))

    def upadate_dimentions(self) -> None:
        self.blit_area_rect.w = self.style.bodyr.w
        self.blit_area_rect.h = self.style.bodyr.h
        if self.style.width > 0:
            self.style.bodyr.w = self.style.width
            self.blit_area_rect.w = self.style.width
        if self.style.height > 0:
            self.style.bodyr.h = self.style.height
            self.blit_area_rect.h = self.style.height
        self.style.paddingr.w = self.style.bodyr.w + self.style.padding.x
        self.style.paddingr.h = self.style.bodyr.h + self.style.padding.y

        self.style.borderr.w = self.style.paddingr.w + self.style.border.x
        self.style.borderr.h = self.style.paddingr.h + self.style.border.y

        self.style.marginr.w = self.style.borderr.w + self.style.margin.x
        self.style.marginr.h = self.style.borderr.h + self.style.margin.y
        print(f"{self.name}: style.width: {self.style.marginr.w}, height: {self.style.marginr.h}")

    def update_on_margin_rect(self) -> None:
        self.style.borderr.x = self.style.marginr.x + self.style.margin.left
        self.style.borderr.y = self.style.marginr.y + self.style.margin.top
        # setting style.padding rect
        self.style.paddingr.x = self.style.borderr.x + self.style.border.left
        self.style.paddingr.y = self.style.borderr.y + self.style.border.top
        # setting body rect
        self.style.bodyr.x = self.style.paddingr.x + self.style.padding.left
        self.style.bodyr.y = self.style.paddingr.y + self.style.padding.top

    def define_structure(self, startx: int, starty: int):
        self.define_totalrect()
        self.style.marginr.x = (startx)
        self.style.marginr.y = (starty)
        
        self.update_on_margin_rect()

        estartx = self.style.bodyr.x
        estarty = self.style.bodyr.y
        pesy = estarty
        if hasattr(self, "elements"):
            for e in self.elements:
                # assuming divs go down like columns
                e.define_structure(estartx, estarty)
                estartx += 0 # e.srect.w
                estarty += e.style.marginr.h
                pesy = estarty

    def define_totalrect(self) -> None:
        self.upadate_dimentions()
    def draw(self, surface: pygame.Surface):
        ...
"""
style attributes needed:
Text Properties


    color: Sets the color of the text.
    font-family: Specifies the font of the text.

    font-size: Sets the size of the text.
    font-weight: Sets the weight (boldness) of the text.
    font-style: Sets the style of the font (e.g., normal, italic, oblique).
    text-align: Sets the horizontal alignment of the text (left, right, center, justify).
    text-decoration: Adds decorations to the text (underline, overline, line-through).
    text-transform: Controls the capitalization of text (uppercase, lowercase, capitalize).
    line-height: Sets the space between lines of text.
    letter-spacing: Sets the space between characters.
    word-spacing: Sets the space between words.

    text-shadow: Adds shadow to the text.

Box Model Properties

    width: Sets the width of the element.
    height: Sets the height of the element.
    max-width: Sets the maximum width of the element.
    min-width: Sets the minimum width of the element.

    max-height: Sets the maximum height of the element.
    min-height: Sets the minimum height of the element.

    margin: Sets the margin around the element.
    margin-top: Sets the top margin.
    margin-right: Sets the right margin.
    margin-bottom: Sets the bottom margin.
    margin-left: Sets the left margin.
    padding: Sets the padding inside the element.
    padding-top: Sets the top padding.
    padding-right: Sets the right padding.
    padding-bottom: Sets the bottom padding.
    padding-left: Sets the left padding.
    border: Sets the border around the element.
    border-width: Sets the width of the border.
    border-style: Sets the style of the border (solid, dotted, dashed, etc.).
    border-color: Sets the color of the border.
    border-radius: Sets the rounded corners of the border.
    box-shadow: Adds shadow around the element.
    box-sizing: Specifies how the width and height of an element are calculated (border-box, content-box).

Background Properties

    background: A shorthand property for setting background-color, background-image, background-repeat, background-attachment, and background-position.
    background-color: Sets the background color of the element.
    background-image: Sets the background image for the element.
    background-repeat: Sets if/how the background image will be repeated (repeat, repeat-x, repeat-y, no-repeat).
    background-attachment: Sets whether the background image scrolls with the page (scroll, fixed, local).
    background-position: Sets the initial position of the background image.
    background-size: Specifies the size of the background images.
    background-clip: Specifies the painting area of the background.
    background-origin: Specifies the origin position of the background.

Positioning Properties

    position: Specifies the type of positioning method used for an element (static, relative, absolute, fixed, sticky).
    top: For positioned elements, sets the top position.
    right: For positioned elements, sets the right position.
    bottom: For positioned elements, sets the bottom position.
    left: For positioned elements, sets the left position.
    z-index: Sets the stack order of an element.

Display and Visibility Properties

    display: Sets the display behavior of an element (block, inline, inline-block, none, flex, grid).
    visibility: Specifies whether the element is visible or not.

    overflow: Specifies what happens if content overflows an element's box (visible, hidden, scroll, auto).
    overflow-x: Specifies what happens if content overflows the left and right edges of an element's box.

    overflow-y: Specifies what happens if content overflows the top and bottom edges of an element's box.
    opacity: Sets the opacity level for an element.

Flexbox Properties


    flex: A shorthand property for setting the flex-grow, flex-shrink, and flex-basis.
    flex-direction: Sets the direction of the flexible items (row, row-reverse, column, column-reverse).
    flex-wrap: Specifies whether the flexible items should wrap or not (nowrap, wrap, wrap-reverse).

    justify-content: Aligns the flexible container's items when the items do not use all available space (flex-start, flex-end, center, space-between, space-around, space-evenly).
    align-items: Aligns the flexible container's items (stretch, flex-start, flex-end, center, baseline).
    align-self: Specifies the alignment for a selected item inside a flexible container.
    align-content: Modifies the behavior of the flex-wrap property (stretch, flex-start, flex-end, center, space-between, space-around).
    order: Sets the order of the flexible item.

Grid Properties

    grid-template-columns: Defines the columns of the grid.
    grid-template-rows: Defines the rows of the grid.
    grid-template-areas: Defines a grid template by referencing the names of the grid areas.
    grid-template: A shorthand property for setting grid-template-rows, grid-template-columns, and grid-template-areas.
    grid-column-gap: Specifies the size of the gap between columns.
    grid-row-gap: Specifies the size of the gap between rows.
    grid-gap: A shorthand property for setting both the row and column gap.
    grid-auto-rows: Specifies the size of an implicitly-created grid row track.
    grid-auto-columns: Specifies the size of an implicitly-created grid column track.
    grid-auto-flow: Controls how the auto-placement algorithm works.
    grid-column-start: Specifies where to start the grid item.
    grid-column-end: Specifies where to end the grid item.
    grid-row-start: Specifies where to start the grid item.
    grid-row-end: Specifies where to end the grid item.
    grid-column: A shorthand property for grid-column-start and grid-column-end.
    grid-row: A shorthand property for grid-row-start and grid-row-end.
    grid-area: A shorthand property for grid-row-start, grid-column-start, grid-row-end, and grid-column-end.


Animation and Transition Properties

    animation: A shorthand property for setting all animation properties.
    animation-name: Specifies the name of the @keyframes animation.
    animation-duration: Specifies how long an animation should take to complete one cycle.
    animation-timing-function: Specifies the speed curve of the animation.
    animation-delay: Specifies a delay before the animation starts.
    animation-iteration-count: Specifies the number of times an animation should be played.
    animation-direction: Specifies whether an animation should be played forwards, backwards or in alternate cycles.
    animation-fill-mode: Specifies a style for the element when the animation is not playing (before it starts, after it ends, or both).
    animation-play-state: Specifies whether the animation is running or paused.
    transition: A shorthand property for setting all the four transition properties.
    transition-property: Specifies the name of the CSS property the transition effect is for.
    transition-duration: Specifies how many seconds or milliseconds a transition effect takes to complete.
    transition-timing-function: Specifies the speed curve of the transition effect.
    transition-delay: Specifies when the transition effect will start.


Other Properties


    cursor: Specifies the type of cursor to be displayed when pointing on an element.
    clip: Clips an absolutely positioned element.

    clip-path: Defines a clipping region to clip the element.
    filter: Defines visual effects (like blur and saturation) to an element.
    resize: Specifies whether or not an element is resizable by the user.
    object-fit: Specifies how the content of a replaced element (like an <img> or <video>) should be resized to fit its container.

    object-position: Specifies the alignment of the replaced element inside its container.

Shorthand Properties

    background: A shorthand property for setting background-color, background-image, background-repeat, background-attachment, and background-position.
    font: A shorthand property for setting font-style, font-variant, font-weight, font-size, line-height, and font-family.
    border: A shorthand property for setting border-width, border-style, and border-color.

    margin: A shorthand property for setting margin-top, margin-right, margin-bottom, and margin-left.
    padding: A shorthand property for setting padding-top, padding-right, padding-bottom, and padding-left.
    list-style: A shorthand property for setting list-style-type, list-style-position, and list-style-image.
    transition: A shorthand property for setting transition-property, transition-duration, transition-timing-function, and transition-delay.

"""
