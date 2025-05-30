
splash_text =r'''
     _           _                                 
    | |         | |                                
  __| |_ __   __| |   ___ __ _ _ ____   ____ _ ___ 
 / _` | '_ \ / _` |  / __/ _` | '_ \ \ / / _` / __|
| (_| | | | | (_| | | (_| (_| | | | \ V / (_| \__ \
 \__,_|_| |_|\__,_|  \___\__,_|_| |_|\_/ \__,_|___/
   by Shahaf Ashash and Simon Labusnky  
'''

usage_text = '''
usage:
M - load map image
T - add token or multiple at mouse position
Ctrl C - copy selected token
Ctrl V - paste copied token at mouse position
G - toggle grid
Ctrl S - save canvas state to file
Ctrl L - load canvas state from file
'''


import json
import os

import tkinter as tk
from tkinter import filedialog

import pygame
from pygame.math import Vector2

from common import CanvasModel, HaloFont
from canvas import Canvas, GridType, Token

from backend.event_queues import PublisherEventQueue
import menu_gui
from canvas_gui import CanvasGui



if __name__ == "__main__":
    pygame.init()
    menu_gui.init()

    print(splash_text)
    print(usage_text)

    # pygame initializations
    message_queue = PublisherEventQueue()

    fps = 60
    fpsClock = pygame.time.Clock()

    width, height = 1920, 1080
    win = pygame.display.set_mode((width, height))

    font_decoration = HaloFont(pygame.font.SysFont('Arial', 32), 2)

    # canvas initializations

    show_grid = False
    copied_token: Token = None

    canvas = Canvas()
    try:
        canvas.set_map_image(r'./assets/maps/swamp.jpg')

    except FileNotFoundError:
        pass

    gui = CanvasGui(canvas, (width, height))

    done = False
    while not done:
        win.fill((0, 0, 0))

        for message in message_queue.get():
            event = message.event
            extra = message.extra

            if event.type == pygame.QUIT:
                done = True

            gui.handle_event(message)
            canvas.handle_event(message)

            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                # Open a file dialog to browse for an image
                root = tk.Tk()
                root.withdraw()  # Hide the root window
                file_path = filedialog.askopenfilename(
                    title="Select Map Image",
                    filetypes=[("Image Files", "*.jfif;*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
                )

                if file_path:
                    canvas.set_map_image(file_path)
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_t:
                # Open a file dialog to browse for multiple images
                mouse_pos = Vector2(pygame.mouse.get_pos())
                root = tk.Tk()
                root.withdraw()  # Hide the root window
                file_paths = filedialog.askopenfilenames(
                    title="Select Map Images",
                    filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
                )

                if file_paths:
                    offset = Vector2(100, 0)
                    for i, file_path in enumerate(file_paths):
                        canvas.add_token(file_path, mouse_pos + offset * i)

            if event.type == pygame.KEYDOWN and event.key == pygame.K_a:
                token = canvas.get_selected_token()
                if token is None:
                    continue

            if event.type == pygame.KEYDOWN and event.key == pygame.K_g:
                show_grid = not show_grid
                grid_type = GridType.NONE if not show_grid else GridType.SQUARE
                canvas.set_grid_type(grid_type)

            if event.type == pygame.KEYDOWN and event.mod & pygame.KMOD_CTRL:
                # token decorations
                if pygame.K_0 <= event.key <= pygame.K_9:
                    token = canvas.get_selected_token()
                    if token is None:
                        continue

                    number_pressed = event.key - pygame.K_0
                    token.add_decoration(font_decoration.render(str(number_pressed), True, (255, 255, 255)))
            
                if event.key == pygame.K_c:
                    # copy selected token
                    token = canvas.get_selected_token()
                    if token is None:
                        continue
                    copied_token = token
                    print('copied')

                elif event.key == pygame.K_v:
                    # paste copied token
                    if copied_token is None:
                        continue
                    mouse_pos = Vector2(pygame.mouse.get_pos())
                    token_model = copied_token.get_current_state()
                    canvas.add_token(token_model.path, mouse_pos)

                elif event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                    # save canvas state to file
                    model = canvas.get_current_state()
                    with open('canvas_save.json', "w") as f:
                        json.dump(model.model_dump(), f, indent=4)
                
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_l:
                    # load canvas state from file
                    if not os.path.exists('canvas_save.json'):
                        continue
                    with open('canvas_save.json', 'r') as f:
                        data = f.read()
                    model = CanvasModel.model_validate_json(data)
                    canvas.load_state(model)
        

            


        # step
        canvas.step()
        gui.step()

        # draw
        canvas.draw(win)
        gui.draw(win)


        pygame.display.flip()
        fpsClock.tick(fps)

    pygame.quit()