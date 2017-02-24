import io
import os
import re
from kug import binary, data, util
from typing import Optional, Tuple, Dict, Iterator


_DATA_NAME_REGEX = r'(\d+),(\d+) (\w+)'


def _parse_ini(content: str) -> Dict:
    ret: Dict = {}
    lines = content.replace('\r', '').split('\n')
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


def _iterate(handle: io.BufferedReader, use_content: bool) -> Iterator[Tuple]:
    handle.seek(0, os.SEEK_END)
    size = handle.tell()
    handle.seek(0)

    while handle.tell() < size:
        name = binary.read_zero_string(handle)
        content_size = binary.read_u32(handle)
        if use_content:
            content = handle.read(content_size)
        else:
            handle.seek(content_size, io.SEEK_CUR)
            content = None

        matches = re.match(_DATA_NAME_REGEX, name)
        assert matches, 'Corrupt game data'

        x = int(matches.group(1))
        y = int(matches.group(2))
        name = matches.group(3)
        assert x >= 0, 'Negative map coordinates'
        assert y >= 0, 'Negative map coordinates'

        yield (x, y, name, content)


def read_world(game_dir: str, geometry: Optional[util.Geometry]) -> data.World:
    world_bin_path = os.path.join(game_dir, 'World.bin')
    with open(world_bin_path, 'rb') as handle:
        min_x = min(coord[0] for coord in _iterate(handle, False))
        max_x = max(coord[0] for coord in _iterate(handle, False))
        min_y = min(coord[1] for coord in _iterate(handle, False))
        max_y = max(coord[1] for coord in _iterate(handle, False))
        width = max_x + 1 - min_x
        height = max_y + 1 - min_y

        world = data.World(game_dir, width, height)
        for x, y, name, content in _iterate(handle, True):
            if geometry and x < geometry.min_x: continue
            if geometry and x > geometry.max_x: continue
            if geometry and y < geometry.min_y: continue
            if geometry and y > geometry.max_y: continue

            if name == 'Sprites':
                world[x, y].sprites = _parse_ini(content.decode('utf-8'))
            elif name == 'Tiles':
                world[x, y].tiles = _parse_ini(content.decode('utf-8'))
            elif name == 'Objects':
                world[x, y].objects = _parse_ini(content.decode('utf-8'))
            elif name == 'Script':
                world[x, y].script = content.decode('cp1250')
            elif name == 'Settings':
                world[x, y].settings = _parse_ini(content.decode('utf-8'))
            elif name == 'Robots':
                world[x, y].robots = _parse_ini(content.decode('utf-8'))
            else:
                raise ValueError('Unknown room data')

    objects_ini_path = os.path.join(game_dir, 'Objects', 'Objects.ini')
    with open(objects_ini_path, 'r', encoding='cp1250') as handle:
        world.objects = _parse_ini(handle.read())

    return world
