from kug.util import range2d
from typing import Any, Optional, Tuple, Dict


class RoomData:
    def __init__(self, x: int, y: int) -> None:
        self.x: int = x
        self.y: int = y
        self.objects: Any = None
        self.robots: Any = None
        self.script: Any = None
        self.settings: Any = None
        self.sprites: Any = None
        self.tiles: Any = None

    @property
    def pos(self) -> Tuple[int, int]:
        return (self.x, self.y)


class World:
    def __init__(self, game_dir: str, width: int, height: int) -> None:
        assert width
        assert height
        self.game_dir = game_dir
        self.width = width
        self.height = height
        self.objects: Optional[Dict] = None
        self.room_data: Dict[Tuple[int, int], RoomData] = {}
        for x, y in range2d(self.width + 1, self.height + 1):
            self.room_data[x, y] = RoomData(x, y)

    def __getitem__(self, key):
        return self.room_data[key]
