from typing import List, Optional
import pygame
from element import Element, Margin
import element

class BasicRect(Element):
    def __init__(self, w:int, h:int, color=(255,255,255), parent: Optional['Element'] = None, name:str="BRc") -> None:
        super().__init__(parent, name)
        self.surface = pygame.Surface((w,h))
        self.surface.fill(color)
        self.bodyr = self.surface.get_rect()
        # print("BODY RECT WIDTH, HEIGHT AND COLOR", self.bodyr.w, self.bodyr.h, color)
        # setting border rect
        self.paddingr.w = self.bodyr.w + self.padding.x
        self.paddingr.h = self.bodyr.h + self.padding.y
        # setting padding rect
        self.borderr.w = self.paddingr.w + self.border.x
        self.borderr.h = self.paddingr.h + self.border.y
        # setting body rect
        self.marginr.w = self.borderr.w + self.margin.x
        self.marginr.h = self.borderr.h + self.margin.y
        print(f"{self.name}: MARGIN RECT WIDTH AND HEIGHT", self.marginr.w, self.marginr.h)

        # setting border rect
        self.borderr.x = self.marginr.x + self.margin.left
        self.borderr.y = self.marginr.y + self.margin.top
        # setting padding rect
        self.paddingr.x = self.borderr.x + self.border.left
        self.paddingr.y = self.borderr.y + self.border.top
        # setting body rect
        self.bodyr.x = self.paddingr.x + self.padding.left
        self.bodyr.y = self.paddingr.y + self.padding.top

    def draw(self, surface: pygame.Surface):
        surface.blit(self.surface, self.bodyr.topleft, self.blit_area_rect)

# A Div will always contain the objects in its center
class Div(Element):
    def __init__(self, parent: Optional['Element'] = None, name:str="Div") -> None:
        super().__init__(parent, name=name)
        self.parent: Optional['Element'] = parent
        self.elements: List[Element] = []
        # self.srect: pygame.Rect = pygame.Rect(0,0,0,0)
        self.padding = element.Padding()
        self.margin = element.Margin()

    def define_totalrect(self) -> None:
        # Define own size
        w = 0
        h = 0
        for e in self.elements:
            # defines body rect: will not take in account position or parent rect size for now
            # in future with dynamic stuff, it will check if parent size/minimum is fixed:
            #     if it is, it will take in acount various percentages and such
            #     else it will just use its minimum space
            e.define_totalrect()
            ew = e.marginr.w
            eh = e.marginr.h
            w += ew
            h += eh
        self.bodyr.w = w
        self.bodyr.h = h
        # This calculates width of margin rect
        # Adds:
        #   - body rect width/height
        #   - padding x/y (left+right or top+bottom)
        #   - border x/y (left+right or top+bottom)
        #   - margin x/y (left+right or top+bottom)
        self.upadate_dimentions()

    def add_element(self, element: Element) -> None:
        self.elements.append(element)

    def draw(self, surface: pygame.Surface):
        for e in self.elements:
            e.draw(surface)

class Canvas(Div):
    def __init__(self, w:int, h:int) -> None:
        super().__init__(None, name="Cvs")
        self.surface: pygame.Surface = pygame.Surface((w, h))
        self.rect = self.surface.get_rect()

        self.elements: List[Element] = []
        print("ui-log-Created UI canvas")
        self.pv: List[Element] = []

    def update(self, startx:int=0, starty:int=0) -> None:
        self.define_totalrect()
        # Canvas should be the size of the screen/screen itself.
        # No margin, idealy
        self.marginr.x, self.marginr.y = 0, 0


        # work out body rect coordinates by working from margin rect backwards
        self.borderr.x = self.marginr.x + self.margin.left
        self.paddingr.x = self.borderr.x + self.border.left
        self.bodyr.x = self.paddingr.x + self.padding.left

        self.borderr.y = self.marginr.y + self.margin.top
        self.paddingr.y = self.borderr.y + self.border.top
        self.bodyr.y = self.paddingr.y + self.padding.top

        startx = self.bodyr.x
        starty = self.bodyr.y
        psy = starty
        for e in self.elements:
            e.define_structure(startx, starty)
            # print("here:", e.id, type(e))
            startx += 0 # e.brect.w
            starty += e.marginr.h
            # print(f"---------Height of margin rect: {e.marginr.h}. Previous starty: {psy} Starty: {starty}")
            psy = starty

    def draw(self, surface: pygame.Surface):
        if self.pv != self.elements:
            self.elements = sorted(self.elements, key=lambda x: x.z_index)
            self.pv = self.elements.copy()
            # self.update(0, 0)
            self.define_structure(0, 0)
            print("sorted elements in Canvas:")
            print("\t", end="")
            print(";".join([e.id for e in self.elements]))
            for e in self.elements: e.print()

        for e in self.elements:
            e.draw(surface)


class Button(Element):
    def __init__(self) -> None:
        self.surface: pygame.Surface
        self.rect: pygame.Rect
if __name__ == "__main__":
    pygame.init()
    ssize = (1280, 720)
    s = pygame.display.set_mode(ssize)
    s.fill((0,0,0))

    canvas = Canvas(ssize[0], ssize[1])
    # Creates new padding of x50 and y70
    p = element.Padding()
    p.x=50
    p.y=70
    # canvas.padding = p


    div = Div(parent=canvas)
    div.name = "DIV"
    brect1 = BasicRect(15,200, (0,0,255), parent=div)
    brect1.margin = Margin(x=50, y=50)
    brect1.define_totalrect()
    brect1.name = "blue rect"

    brect2 = BasicRect(500,30, (255,0,125), parent=div)
    brect2.margin = Margin(x=100, y=0)
    brect2.define_totalrect()
    brect2.name = "red  rect"

    # print(brect1.margin)
    # print(brect2.margin)

    div.add_element(brect2)
    div.add_element(brect1)

    br = BasicRect(100, 100, parent=canvas)
    br.width = 10
    br.height = 30

    canvas.add_element(div)
    canvas.add_element(br)

    # canvas.update()

    on = True
    while on:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                on=False
        s.fill((0,0,0))
        canvas.draw(s)
        pygame.display.update()
