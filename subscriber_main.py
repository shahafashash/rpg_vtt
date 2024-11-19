import threading
import uvicorn
from backend.network import server


if __name__ == "__main__":
    from backend.game_logic import PublisherGameLogic, SubscriberGameLogic

    # Create two game logic objects
    p1 = SubscriberGameLogic()

    # Start the game logic objects
    p1.start()

    # Wait for both game logic objects to finish
    p1.join()

    print("process have finished.")
