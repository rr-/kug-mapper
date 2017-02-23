#!/usr/bin/env python3
import os
import argparse
from PIL import Image
from kug.util import range2d, progress, scan_tree, Geometry, parse_geometry
from kug.world_reader import read_world
from kug.render import render_world


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--game-dir', default=(
        '~/.local/share/Steam/steamapps/common/Knytt Underground/World'))
    parser.add_argument('--geometry', default='*')
    parser.add_argument('--render-backgrounds', type=bool, default=False)
    parser.add_argument('--mask-tiles', type=bool, default=True)
    parser.add_argument('--scale', type=int, default=4)
    parser.add_argument('--output-path', type=str, default='map.png')
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    game_dir: str = os.path.expanduser(args.game_dir)
    geometry: Geometry = parse_geometry(args.geometry)
    render_backgrounds: bool = args.render_backgrounds
    mask_tiles: bool = args.mask_tiles
    scale: int = args.scale
    output_path: str = args.output_path

    world = read_world(game_dir, geometry)
    if geometry:
        geometry.min_x = max(0, geometry.min_x)
        geometry.min_y = max(0, geometry.min_y)
        geometry.max_x = min(world.width - 1, geometry.max_x)
        geometry.max_y = min(world.height - 1, geometry.max_y)

    map_image = render_world(world, render_backgrounds, mask_tiles, geometry)
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
