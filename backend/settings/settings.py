from typing import Optional, Dict, Any, Annotated
from os import PathLike
from pathlib import Path
import json
from pydantic import BaseModel, Field, model_validator

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

class AssetsSettings(BaseModel):
    maps: str = Field(
        str(Path(__file__).parent.parent.parent.joinpath('assets/maps').resolve()),
        description='Path to the directory containing the maps'
    )
    tokens: str = Field(
        str(Path(__file__).parent.parent.parent.joinpath('assets/tokens').resolve()),
        description='Path to the directory containing the tokens'
    )
    sound_effects: str = Field(
        str(Path(__file__).parent.parent.parent.joinpath('assets/sound_effects').resolve()),
        description='Path to the directory containing the sound effects'
    )

    @model_validator(mode="before")
    def resolve_paths(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        for field_name, field_type in cls.__annotations__.items():
            if field_name in values and (field_type == str or field_type == Path):
                field_value = values.get(field_name)
                if isinstance(field_value, str):
                    values[field_name] = str(Path(field_value).resolve())
                elif isinstance(field_value, Path):
                    values[field_name] = str(field_value.resolve())
        return values

class GameSettings(BaseModel):
    resolution: ResolutionSettings = Field(ResolutionSettings(), description="Settings related to the game's resolution")
    keyboard: KeyboardSettings = Field(KeyboardSettings(), description="Keyboard settings including key bindings")
    sound: SoundSettings = Field(SoundSettings(), description="Sound settings for the game")
    assets: AssetsSettings = Field(AssetsSettings(), description="Paths to the different assets directories")

class SettingsManager:
    def __init__(self, settings_file: Optional[PathLike] = None) -> None:
        self._settings_file: Path = Path(settings_file).resolve() if settings_file else Path(__file__).parent.joinpath('settings.json').resolve()
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
        settings_folder = Path(__file__).parent.resolve()
        settings_file_path = settings_folder.joinpath('settings.json')
        with settings_file_path.open('w') as f:
            f.write(default_settings.model_dump_json(indent=4))

