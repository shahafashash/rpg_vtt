from __future__ import annotations
from typing import Dict, Any, Optional
import json
from pygame.event import Event as PyGameEvent
from pydantic import BaseModel, Field


class Message(BaseModel):
    event: Optional[PyGameEvent] = Field(default=None)
    extra: Optional[Dict[str, Any]] = Field(default=None)

    class Config:
        arbitrary_types_allowed = True
        extra = "forbid"

    def model_dump_json(self) -> str:
        return json.dumps(
            {
                "event": (
                    {
                        "type": self.event.type,
                        "dict": self.event.__dict__,
                    }
                    if self.event
                    else None
                ),
                "extra": self.extra,
            }
        )

    @classmethod
    def model_validate_json(cls, message_str: str) -> Message:
        message_dict = json.loads(message_str)
        event = message_dict["event"]
        pygame_event = PyGameEvent(event["type"], event["dict"]) if event else None
        return cls(event=pygame_event, extra=message_dict["extra"])
