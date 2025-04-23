
import json
import os

import tkinter as tk
from tkinter import filedialog

import pygame
from pygame.math import Vector2

from common import CanvasModel, HaloFont
from canvas import Canvas

from backend.event_queues import PublisherEventQueue
import menu_gui
from canvas_gui import CanvasGui



if __name__ == "__main__":
    pygame.init()
    menu_gui.init()

    # pygame initializations
    message_queue = PublisherEventQueue()

    fps = 60
    fpsClock = pygame.time.Clock()

    width, height = 1920, 1080
    win = pygame.display.set_mode((width, height))

    font_decoration = HaloFont(pygame.font.SysFont('Arial', 32), 2)

    # canvas initializations

    canvas = Canvas(draw_grid=False)
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

			
            if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                model = canvas.get_current_state()
                with open('canvas_save.json', "w") as f:
                    json.dump(model.model_dump(), f, indent=4)
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_l:
                if not os.path.exists('canvas_save.json'):
                    continue
                with open('canvas_save.json', 'r') as f:
                    data = f.read()
                model = CanvasModel.model_validate_json(data)
                canvas.load_state(model)
            
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
                

            if event.type == pygame.KEYDOWN and event.mod & pygame.KMOD_CTRL:
                if pygame.K_0 <= event.key <= pygame.K_9:
                    token = canvas.get_selected_token()
                    if token is None:
                        continue

                    number_pressed = event.key - pygame.K_0
                    token.add_decoration(font_decoration.render(str(number_pressed), True, (255, 255, 255)))


        # step
        canvas.step()
        gui.step()

        # draw
        canvas.draw(win)
        gui.draw(win)


        pygame.display.flip()
        fpsClock.tick(fps)

    pygame.quit()