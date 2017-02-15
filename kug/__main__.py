#!/usr/bin/env python3
import os
from PIL import Image
from kug.util import range2d, progress, scan_tree
from kug.world import World, RoomData
from kug.world_reader import read_world
from kug.render import render_world


def main() -> None:
    game_dir = os.path.expanduser(
        '~/.local/share/Steam/steamapps/common/Knytt Underground/World')
    debug = True
    render_backgrounds = False
    mask_tiles = True
    scale = 4
    output_path = 'map.png'

    world = read_world(game_dir, debug)
    map_image = render_world(world, render_backgrounds, mask_tiles)
    (
        map_image
        .resize(
            (
                map_image.width // scale,
                map_image.height // scale,
            ),
            Image.ANTIALIAS)
        .save(output_path)
    )


if __name__ == '__main__':
    main()
