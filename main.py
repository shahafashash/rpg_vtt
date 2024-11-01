import threading
import uvicorn
from server import app


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
