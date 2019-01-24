import io
from typing import Any, Dict, List, Optional, Tuple

from kug_mapper import binary, util


class SpriteArchive:
    def __init__(self, path: str, offsets: Dict[int, int]) -> None:
        self._offsets = offsets
        self._path = path
        with open(path, 'rb') as handle:
            handle.seek(0, io.SEEK_END)
            file_size = handle.tell()
            self._all_offsets = list(
                sorted(list(offsets.values()) + [file_size]))

    def __len__(self) -> int:
        return len(self._offsets)

    def read(self, index: int) -> bytes:
        offset = self._offsets[index]
        with open(self._path, 'rb') as handle:
            handle.seek(offset + 16)
            size = [x for x in self._all_offsets if x > offset][0] - offset
            return handle.read(size)


class Room:
    def __init__(self, world: 'World', x: int, y: int) -> None:
        self.world = world
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
        self.room_data: Dict[Tuple[int, int], Room] = {}
        for x, y in util.range2d(self.width + 1, self.height + 1):
            self.room_data[x, y] = Room(self, x, y)

    def __getitem__(self, key):
        return self.room_data[key]

    def __iter__(self):
        return iter(self.room_data.values())
