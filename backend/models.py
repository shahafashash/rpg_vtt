from __future__ import annotations
from typing import Dict, Any, Optional
import json
from pygame.event import Event as PyGameEvent
from pydantic import BaseModel, Field, field_serializer, model_validator


# class Message(BaseModel):

#     event: Optional[PyGameEvent] = Field(default=None)
#     extra: Optional[Dict[str, Any]] = Field(default=None)

#     class Config:
#         arbitrary_types_allowed = True
#         extra = "forbid"

#     @field_serializer('event')
#     def serialize_event(self, event: Optional[PyGameEvent]) -> Optional[Dict[str, Any]]:
#         # Serialize event to a dict
#         if event:
#             return {
#                 "type": event.type,
#                 "dict": event.__dict__,
#             }
#         return None

#     @model_validator(mode="before")
#     def deserialize_event(cls, values: Dict[str, Any]) -> Dict[str, Any]:
#         # This model validator is used to deserialize the event
        
#         event = values.get("event")
#         print('event---:', event)
#         if event:
#             # Recreate the PyGameEvent from the dictionary
#             event_dict = event.dict
#             event_type = event.type
#             if event_type is not None:
#                 event = PyGameEvent(event_type, event_dict)
#                 values["event"] = event
#         return values

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