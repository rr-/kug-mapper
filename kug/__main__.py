#!/usr/bin/env python3
import os
from PIL import Image
from kug.util import range2d, progress, scan_tree
from kug.world import World, RoomData
from kug.world_reader import read_world
from kug.render import render_world


GAME_DIR = os.path.expanduser(
    '~/.local/share/Steam/steamapps/common/Knytt Underground/World')
SCALE = 4
DEBUG = True


def main() -> None:
    world = read_world(GAME_DIR, DEBUG)
    map_image = render_world(world)
    (
        map_image
        .resize(
            (
                map_image.width // SCALE,
                map_image.height // SCALE,
            ),
            Image.ANTIALIAS)
        .save('map.png')
    )


if __name__ == '__main__':
    main()
