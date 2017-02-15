import io
import os
import re
import struct
from kug.world import World
from typing import Tuple, Dict, Iterator


_DATA_NAME_REGEX = r'(\d+),(\d+) (\w+)'


def _read_u8(handle: io.BufferedReader) -> int:
    return struct.unpack('B', handle.read(1))[0]


def _read_u32(handle: io.BufferedReader) -> int:
    return struct.unpack('<L', handle.read(4))[0]


def _read_zero_string(handle: io.BufferedReader) -> str:
    ret = b''
    while True:
        byte = _read_u8(handle)
        if byte == 0:
            break
        ret += bytes([byte])
    return ret.decode('utf-8')


def _parse_ini(data: str) -> Dict:
    ret: Dict = {}
    lines = data.replace('\r', '').split('\n')
    for line in lines:
        match = re.match('^\[(.*)\]$', line)
        if match:
            name, = match.groups()
            ret[name] = current_obj = {}
            continue

        match = re.match('^([^=]+)=(.*)$', line)
        if match:
            key, value = match.groups()
            current_obj[key] = value
            continue

    return ret


def _iterate(handle: io.BufferedReader, use_data: bool) -> Iterator[Tuple]:
    handle.seek(0, os.SEEK_END)
    size = handle.tell()
    handle.seek(0)

    while handle.tell() < size:
        name = _read_zero_string(handle)
        data_size = _read_u32(handle)
        if use_data:
            data = handle.read(data_size)
        else:
            handle.seek(data_size, io.SEEK_CUR)
            data = None

        matches = re.match(_DATA_NAME_REGEX, name)
        assert matches, 'Corrupt game data'

        x = int(matches.group(1))
        y = int(matches.group(2))
        name = matches.group(3)
        assert x >= 0, 'Negative map coordinates'
        assert y >= 0, 'Negative map coordinates'

        yield (x, y, name, data)


def read_world(game_dir: str, debug: bool) -> World:
    world_bin_path = os.path.join(game_dir, 'World.bin')
    with open(world_bin_path, 'rb') as handle:
        width = 0
        height = 0
        for x, y, name, data in _iterate(handle, False):
            width = max(width, x)
            height = max(height, y)

        if debug:
            width = min(width, 10)
            height = min(height, 10)

        world = World(width, height)
        for x, y, name, data in _iterate(handle, True):
            if y > height: continue
            if x > width: continue
            if name == 'Sprites':
                world[x, y].sprites = _parse_ini(data.decode('utf-8'))
            elif name == 'Tiles':
                world[x, y].tiles = _parse_ini(data.decode('utf-8'))
            elif name == 'Objects':
                world[x, y].objects = _parse_ini(data.decode('utf-8'))
            elif name == 'Script':
                world[x, y].script = data.decode('cp1250')
            elif name == 'Settings':
                world[x, y].settings = _parse_ini(data.decode('utf-8'))
            elif name == 'Robots':
                world[x, y].robots = _parse_ini(data.decode('utf-8'))
            else:
                raise ValueError('Unknown room data')

    objects_ini_path = os.path.join(game_dir, 'Objects', 'Objects.ini')
    with open(objects_ini_path, 'r', encoding='cp1250') as handle:
        world.objects = _parse_ini(handle.read())

    return world
