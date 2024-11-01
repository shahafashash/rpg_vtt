from pygame.mixer import Sound


class SoundEffect:
    def __init__(self, sound_file: str) -> None:
        self._sound_file: str = sound_file
        self._sound: Sound = self._load_sound(sound_file)
        self._volume: float = 1.0

    def _load_sound(self, sound_file: str) -> Sound:
        return Sound(sound_file)

    def play(self, loops: int = 0) -> None:
        self._sound.play(loops=loops)

    def stop(self) -> None:
        self._sound.stop()

    def set_volume(self, volume: float) -> None:
        self._volume = max(0.0, min(1.0, volume))
        self._sound.set_volume(self._volume)

    def get_volume(self) -> float:
        return self._volume


class LoopingSoundEffect(SoundEffect):
    def play(self, loops: int = -1) -> None:
        super().play(loops=loops)
