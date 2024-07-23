from typing import List, Optional, Tuple
import pygame
from element import Element, Margin
import element
import cssutils



class BasicRect(Element):
    def __init__(self, w:int, h:int, color=(255,255,255), parent: Optional['Element'] = None, name:str="BRc") -> None:
        super().__init__(parent, name)
        self.surface = pygame.Surface((w,h))
        self.surface.fill(color)
        self.style.bodyr = self.surface.get_rect()

        # setting style.border rect
        self.style.paddingr.w = self.style.bodyr.w + self.style.padding.x
        self.style.paddingr.h = self.style.bodyr.h + self.style.padding.y
        # setting style.padding rect
        self.style.borderr.w = self.style.paddingr.w + self.style.border.x
        self.style.borderr.h = self.style.paddingr.h + self.style.border.y
        # setting body rect
        self.style.marginr.w = self.style.borderr.w + self.style.margin.x
        self.style.marginr.h = self.style.borderr.h + self.style.margin.y

        # setting style.border rect
        self.style.borderr.x = self.style.marginr.x + self.style.margin.left
        self.style.borderr.y = self.style.marginr.y + self.style.margin.top
        # setting style.padding rect
        self.style.paddingr.x = self.style.borderr.x + self.style.border.left
        self.style.paddingr.y = self.style.borderr.y + self.style.border.top
        # setting body rect
        self.style.bodyr.x = self.style.paddingr.x + self.style.padding.left
        self.style.bodyr.y = self.style.paddingr.y + self.style.padding.top

    def draw(self, surface: pygame.Surface):
        surface.blit(self.surface, self.style.bodyr.topleft, self.blit_area_rect)

class Paragraph(Element):
    def __init__(self, text:str="", font_family:str="arial", font_size:int=32, color:Tuple[int,int,int]|str=(255,255,255), parent: Optional['Element'] = None, name:str="BRc") -> None:
        super().__init__(parent, name)
        self.font: pygame.font.Font|None = element.fonts.get((font_family, font_size), None)
        if not self.font:
            try:
                print("WARN: couldn't get font. trying to load it from \"pygame\"")
                f = pygame.font.Font(pygame.font.match_font(font_family), font_size)
                element.fonts[(font_family, font_size)] = f
            except Exception as e:
                print(f"ERROR: {e}\n\tSetting font to \"arial\":32")
                self.font = element.fonts[("arial", 32)]
        if not self.font:
            raise Exception(f"Missing font for Paragraph: {self.element_id}")

        self.surface = self.font.render(text, True, color)
        self.style.bodyr = self.surface.get_rect()

        # setting style.border rect
        self.style.paddingr.w = self.style.bodyr.w + self.style.padding.x
        self.style.paddingr.h = self.style.bodyr.h + self.style.padding.y
        # setting style.padding rect
        self.style.borderr.w = self.style.paddingr.w + self.style.border.x
        self.style.borderr.h = self.style.paddingr.h + self.style.border.y
        # setting body rect
        self.style.marginr.w = self.style.borderr.w + self.style.margin.x
        self.style.marginr.h = self.style.borderr.h + self.style.margin.y

        # setting style.border rect
        self.style.borderr.x = self.style.marginr.x + self.style.margin.left
        self.style.borderr.y = self.style.marginr.y + self.style.margin.top
        # setting style.padding rect
        self.style.paddingr.x = self.style.borderr.x + self.style.border.left
        self.style.paddingr.y = self.style.borderr.y + self.style.border.top
        # setting body rect
        self.style.bodyr.x = self.style.paddingr.x + self.style.padding.left
        self.style.bodyr.y = self.style.paddingr.y + self.style.padding.top

    def draw(self, surface: pygame.Surface):
        surface.blit(self.surface, self.style.bodyr.topleft, self.blit_area_rect)

# A Div will always contain the objects in its center
class Div(Element):
    def __init__(self, parent: Optional['Element'] = None, name:str="Div") -> None:
        super().__init__(parent, name=name)
        self.parent: Optional['Element'] = parent
        self.elements: List[Element] = []
        # self.srect: pygame.Rect = pygame.Rect(0,0,0,0)
        self.style.padding = element.Padding()
        self.style.margin = element.Margin()

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
            ew = e.style.marginr.w
            eh = e.style.marginr.h
            w += ew
            h += eh
        self.style.bodyr.w = w
        self.style.bodyr.h = h
        # This calculates style.width of style.margin rect
        # Adds:
        #   - body rect style.width/height
        #   - style.padding x/y (left+right or top+bottom)
        #   - style.border x/y (left+right or top+bottom)
        #   - style.margin x/y (left+right or top+bottom)
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
        # No style.margin, idealy
        self.style.marginr.x, self.style.marginr.y = 0, 0


        # work out body rect coordinates by working from style.margin rect backwards
        self.style.borderr.x = self.style.marginr.x + self.style.margin.left
        self.style.paddingr.x = self.style.borderr.x + self.style.border.left
        self.style.bodyr.x = self.style.paddingr.x + self.style.padding.left

        self.style.borderr.y = self.style.marginr.y + self.style.margin.top
        self.style.paddingr.y = self.style.borderr.y + self.style.border.top
        self.style.bodyr.y = self.style.paddingr.y + self.style.padding.top

        startx = self.style.bodyr.x
        starty = self.style.bodyr.y
        psy = starty
        for e in self.elements:
            e.define_structure(startx, starty)
            # print("here:", e.element_id, type(e))
            startx += 0 # e.brect.w
            starty += e.style.marginr.h
            # print(f"---------Height of style.margin rect: {e.style.marginr.h}. Previous starty: {psy} Starty: {starty}")
            psy = starty

    def draw(self, surface: pygame.Surface):
        if self.pv != self.elements:
            self.elements = sorted(self.elements, key=lambda x: x.style.z_index)
            self.pv = self.elements.copy()
            # self.update(0, 0)
            self.define_structure(0, 0)
            print("sorted elements in Canvas:")
            print("\t", end="")
            print(";".join([e.element_id for e in self.elements]))
            for e in self.elements: e.print()

        for e in self.elements:
            e.draw(surface)


class Button(Element):
    def __init__(self) -> None:
        self.surface: pygame.Surface
        self.rect: pygame.Rect

"""
-Little nice extra thingy:
import cssutils

css = "body { font-size: 14px; color: black; }"
sheet = cssutils.parseString(css)
for rule in sheet:
    if rule.type == rule.STYLE_RULE:
        print(rule.selectorText, rule.style.cssText)
"""
if __name__ == "__main__":
    pygame.init()
    ssize = (1280, 720)
    s = pygame.display.set_mode(ssize)
    s.fill((0,0,0))

    font_size = 32
    font = pygame.font.Font(pygame.font.match_font('arial'), font_size)
    element.fonts[("arial", 32)] = font

    canvas = Canvas(ssize[0], ssize[1])
    # Creates new style.padding of x50 and y70
    p = element.Padding()
    p.x=50
    p.y=70
    # canvas.style.padding = p


    div = Div(parent=canvas)
    div.name = "DIV"
    brect1 = BasicRect(15,200, (0,0,255), parent=div)
    brect1.style.margin = Margin(x=50, y=50)
    brect1.define_totalrect()
    brect1.name = "blue rect"
    p1 = Paragraph(text="Hello World!")

    brect2 = BasicRect(500,30, (255,0,125), parent=div)
    brect2.style.margin = Margin(x=100, y=0)
    brect2.define_totalrect()
    brect2.name = "red  rect"

    # print(brect1.style.margin)
    # print(brect2.style.margin)

    div.add_element(brect1)
    div.add_element(p1)
    div.add_element(brect2)

    br = BasicRect(100, 100, parent=canvas)
    br.style.width = 10
    br.style.height = 30

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
