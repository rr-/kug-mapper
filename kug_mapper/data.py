import io
import typing as T

from kug_mapper import binary, util


class SpriteArchive:
    def __init__(self, path: str, offsets: T.Dict[int, int]) -> None:
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
        self.objects: T.Any = None
        self.robots: T.Any = None
        self.script: T.Any = None
        self.settings: T.Any = None
        self.sprites: T.Any = None
        self.tiles: T.Any = None

    @property
    def pos(self) -> T.Tuple[int, int]:
        return (self.x, self.y)


class World:
    def __init__(self, game_dir: str, width: int, height: int) -> None:
        assert width
        assert height
        self.game_dir = game_dir
        self.width = width
        self.height = height
        self.objects: T.Optional[T.Dict[str, T.Dict[str, T.Any]]] = None
        self.room_data: T.Dict[T.Tuple[int, int], Room] = {}
        for x, y in util.range2d(self.width + 1, self.height + 1):
            self.room_data[x, y] = Room(self, x, y)

    def __getitem__(self, key: T.Tuple[int, int]) -> T.Any:
        return self.room_data[key]

    def __iter__(self) -> T.Iterator[Room]:
        return iter(self.room_data.values())
