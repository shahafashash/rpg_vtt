
from math import pi, cos, sin

import pygame
from pygame.math import Vector2


def draw_grid_square(surf: pygame.Surface, pos: Vector2, size=50, color=(0,0,0)):
        width, height = surf.get_size()

        i = pos[0]
        while i < width:
            pygame.draw.line(surf, color, (i, 0), (i, height))
            i += size

        i = pos[1]
        while i < height:
            pygame.draw.line(surf, color, (0, i), (width, i))
            i += size

def draw_grid_hex(surf: pygame.Surface, size=50, color=(0,0,0)):
    a = size
    b = a * cos(pi / 3)
    c = a * sin(pi / 3)
    lines = [
        [(b, 2 * c), (0, c), (b, 0), (a + b, 0), (2 * b + a, c), (a + b, 2 * c)],
        [(2 * b + a, c), (2 * b + 2 * a, c)],
    ]

    for y in range(0, surf.get_height(), int(2 * c)):
        for x in range(0, surf.get_width(), int(2 * b + 2 * a)):
            for line in lines:
                line_offset = [(t[0] + x, t[1] + y) for t in line]
                pygame.draw.lines(surf, color, False, line_offset)