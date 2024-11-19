

import pygame
from pygame import Vector2

DARK_COLOR = (0, 0, 0)

class ObscuringRect:
    def __init__(self):
        self.pos1 = Vector2()
        self.pos2 = Vector2()
    
    def handle_event(self, event):
        pass

    def draw(self, win):
        pygame.draw.rect(win, DARK_COLOR, (self.pos1, self.pos2 - self.pos1))


class Obscurers:
    def __init__(self):
        self.rects = []
    


