
import json
import os
from random import randint

import tkinter as tk
from tkinter import filedialog

import pygame
from pygame.math import Vector2

from common import CanvasModel
from canvas import Canvas

from backend.event_queues import PublisherEventQueue
import menu_gui
from canvas_gui import CanvasGui


pygame.init()
menu_gui.init()

# pygame initializations
message_queue = PublisherEventQueue()

fps = 60
# fpsClock = pygame.time.Clock()

width, height = 1920, 1080
# win = pygame.display.set_mode((width, height))

# canvas initializations

canvas = Canvas()


gui = CanvasGui(canvas, (width, height))

# tests

# load map 

# load map with no file
try:
    canvas.set_map_image(r'no map file')
except FileNotFoundError:
    pass
except Exception as e:
    assert False, f"Unexpected error: {e}"

# create and load temp map
temp_map_path = r'./assets/maps/temp_map.png'
map_surf = pygame.Surface((1024, 1024))
map_surf.fill((255, 0, 0))
pygame.image.save(map_surf, temp_map_path)

canvas.set_map_image(temp_map_path)

# create and load tokens
for i in range(10):
    surf = pygame.Surface((64, 64))
    surf.fill([randint(0, 255) for _ in range(3)])
    path = f'./assets/token_{i}.png'
    pygame.image.save(surf, path)

for i in range(10):
    path = f'./assets/token_{i}.png'
    canvas.add_token(path, (randint(100, 900), randint(100, 900)))

# save
state_1 = canvas.get_current_state()

# remove tokens
canvas.tokens.clear()

state_2 = canvas.get_current_state()
assert state_1 != state_2, "State should be different after removing tokens"

# load state
canvas.load_state(state_1)

state_3 = canvas.get_current_state()
assert state_1 == state_3, "State should be the same after loading"

canvas.tokens[3].pos = Vector2(884.55558, 112.5568)
canvas.transform.pos = Vector2(1.555555, 2.447555)
state_4 = canvas.get_current_state()

print('all well')
