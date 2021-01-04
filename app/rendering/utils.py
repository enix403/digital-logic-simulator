from __future__ import annotations
from pygame import gfxdraw
from pygame import freetype

freetype.init()


def draw_circle(surface, x, y, radius, color):
    gfxdraw.aacircle(surface, x, y, radius, color)
    gfxdraw.filled_circle(surface, x, y, radius, color)


def render_text(font, text, size, fgcolor, bgcolor=(0, 0, 0, 0)):
    txt_surface, _ = font.render(text, fgcolor, bgcolor, freetype.STYLE_DEFAULT, 0, size)
    return txt_surface

