from __future__ import annotations
from typing import Dict, Any, Optional
import json
from pygame.event import Event as PyGameEvent
from pydantic import BaseModel, Field, field_serializer, model_validator


class Message(BaseModel):

    event: Optional[PyGameEvent] = Field(default=None)
    extra: Optional[Dict[str, Any]] = Field(default=None)

    class Config:
        arbitrary_types_allowed = True
        extra = "forbid"

    @field_serializer('event')
    def serialize_event(self, event: Optional[PyGameEvent]) -> Optional[Dict[str, Any]]:
        # Serialize event to a dict
        if event:
            return {
                "type": event.type,
                "dict": event.__dict__,
            }
        return None

    @model_validator(mode="before")
    def deserialize_event(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        # This model validator is used to deserialize the event
        event_data = values.get("event")
        if event_data:
            # Recreate the PyGameEvent from the dictionary
            event_dict = event_data.get("dict", {})
            event_type = event_data.get("type")
            if event_type is not None:
                event = PyGameEvent(event_type, event_dict)
                values["event"] = event
        return values

