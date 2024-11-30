
import json

import pygame
from pygame.math import Vector2

from common import CanvasModel
from canvas import Canvas

from backend.event_queues import PublisherEventQueue
from canvas_gui import CanvasGui


if __name__ == "__main__":
    pygame.init()

    # pygame initializations
    message_queue = PublisherEventQueue()

    fps = 60
    fpsClock = pygame.time.Clock()

    width, height = 1280, 720
    win = pygame.display.set_mode((width, height))

    # canvas initializations

    canvas = Canvas()
    canvas.set_map_image(r'./assets/maps/image_31.jfif')

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