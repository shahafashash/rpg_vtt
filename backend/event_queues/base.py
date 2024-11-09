from typing import List
from abc import ABC, abstractmethod

class EventQueue(ABC):
    @abstractmethod
    def get(self) -> List[str]:
        pass
