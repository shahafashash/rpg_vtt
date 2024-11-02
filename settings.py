from typing import Optional, Dict, Any, Annotated
from os import PathLike
from pathlib import Path
import json
from pydantic import BaseModel, Field

PositiveInt = Annotated[int, Field(gt=0)]
PositiveDecimal = Annotated[float, Field(gt=0)]
NonEmptyStr = Annotated[str, Field(min_length=1)]


class ResolutionSettings(BaseModel):
    width: PositiveInt = Field(1280, description="Width of the game window")
    height: PositiveInt = Field(720, description="Height of the game window")
    fullscreen: bool = Field(False, description="Enable fullscreen mode")


class KeyboardSettings(BaseModel):
    keybindings: Dict[str, NonEmptyStr] = Field(
        {}, description="Mapping of action names to key bindings"
    )


class SoundSettings(BaseModel):
    master_volume: float = Field(1.0, ge=0.0, le=1.0, description="Master volume level (0.0 to 1.0)")
    music_volume: float = Field(1.0, ge=0.0, le=1.0, description="Music volume level (0.0 to 1.0)")
    sfx_volume: float = Field(1.0, ge=0.0, le=1.0, description="Sound effects volume level (0.0 to 1.0)")
    mute: bool = Field(False, description="Mute all sounds")


class GameSettings(BaseModel):
    resolution: ResolutionSettings = Field(ResolutionSettings(), description="Settings related to the game's resolution")
    keyboard: KeyboardSettings = Field(KeyboardSettings(), description="Keyboard settings including key bindings")
    sound: SoundSettings = Field(SoundSettings(), description="Sound settings for the game")


class SettingsManager:
    def __init__(self, settings_file: Optional[PathLike] = "settings.json") -> None:
        self._settings_file: Path = Path(settings_file).resolve()
        self._settings: GameSettings = self._load_settings()

    @property
    def settings(self) -> GameSettings:
        return self._settings

    def _load_settings(self) -> GameSettings:
        if not self._settings_file.exists():
            self._create_default_settings()

        with self._settings_file.open('r') as f:
            settings_data = json.load(f)

        return GameSettings(**settings_data)

    def _create_default_settings(self) -> None:
        default_settings = GameSettings()
        with open("settings.json", "w") as f:
            f.write(default_settings.model_dump_json(indent=4))

