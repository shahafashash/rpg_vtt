import multiprocessing
import threading
import time
from math import sin, cos

import pygame

from event_queue import PublisherEventQueue, SubscriberEventQueue
from publisher import Publisher
from subscriber import Subscriber
import custom_events as CustomPyGameEvents
import uvicorn
from server import app


# Function for Subscriber
def subscriber_process():
    subscriber = Subscriber()
    event_queue = SubscriberEventQueue(subscriber)
    subscriber.start()

    pygame.init()
    win = pygame.display.set_mode((600, 300))
    pygame.display.set_caption("Subscriber")
    clock = pygame.time.Clock()

    timer = 0
    play_circle = True

    done = False
    while not done:
        # pygame event handling
        for message in event_queue.get():
            event = message.event
            if event.type == pygame.QUIT:
                print("quit 1")
                done = True
            if event.type == CustomPyGameEvents.CIRCLE_INTERACT:
                print("got space")
                play_circle = not play_circle

        # Game logic
        if play_circle:
            timer += 1

        # Drawing code
        win.fill((255, 0, 0))  # Clear the screen with white

        pygame.draw.circle(
            win,
            (0, 255, 0),
            (200 + 50 * cos(timer * 0.1), 200 + 50 * sin(timer * 0.1)),
            35,
        )
        # Add drawing code here

        # Update the display
        pygame.display.update()

        # Frame rate
        clock.tick(60)

    subscriber.stop()
    pygame.quit()


# Function for Publisher
def publisher_process():
    publisher = Publisher()
    event_queue = PublisherEventQueue()
    publisher.start()

    pygame.init()
    win = pygame.display.set_mode((500, 260))
    pygame.display.set_caption("Publisher")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("Arial", 18)
    text = font.render(
        "press space in this window to control ball on other window", True, (0, 0, 0)
    )

    play_circle = True

    done = False
    while not done:
        # Event handling
        for message in event_queue.get():
            event = message.event
            if event.type == pygame.QUIT:
                publisher.publish(event=event)
                print("quit 2")
                done = True

            if event.type == CustomPyGameEvents.CIRCLE_INTERACT:
                publisher.publish(event=event)
                play_circle = not play_circle

        # Game logic

        # Drawing code
        win.fill((0, 255, 0))  # Clear the screen with white
        win.blit(text, (0, 0))
        # Add drawing code here

        # Update the display
        pygame.display.update()

        # Frame rate
        clock.tick(60)

    publisher.stop()
    pygame.quit()


if __name__ == "__main__":
    from game_logic import PublisherGameLogic, SubscriberGameLogic

    uvicorn_thread = threading.Thread(
        target=uvicorn.run, args=(app,), kwargs={"port": 8000}, daemon=True
    ).start()

    # Create two game logic objects
    p1 = SubscriberGameLogic()
    p2 = PublisherGameLogic()

    # Start the game logic objects
    p1.start()
    p2.start()

    # Wait for both game logic objects to finish
    p1.join()
    p2.join()

    print("Both processes have finished.")
