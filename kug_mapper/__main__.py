#!/usr/bin/env python3
import argparse
import os

from PIL import Image

from kug_mapper import data_reader, renderer, util


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument('--game-dir', default=(
        '~/.local/share/Steam/steamapps/common/Knytt Underground/World'))
    parser.add_argument('--output-path', type=str, default='map.png')
    parser.add_argument('--geometry', default='*')
    parser.add_argument('--scale', type=int, default=4)
    parser.add_argument('--backgrounds-opacity', type=float, default=0.0)
    parser.add_argument('--objects-opacity', type=float, default=0.0)
    parser.add_argument('--tiles-opacity', type=float, default=0.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    game_dir: str = os.path.expanduser(args.game_dir)
    geometry: util.Geometry = util.parse_geometry(args.geometry)
    backgrounds_opacity: float = args.backgrounds_opacity
    objects_opacity: float = args.objects_opacity
    tiles_opacity: float = args.tiles_opacity
    scale: int = args.scale
    output_path: str = args.output_path

    assert 0.0 <= backgrounds_opacity <= 1.0
    assert 0.0 <= objects_opacity <= 1.0
    assert 0.0 <= tiles_opacity <= 1.0

    sprites = data_reader.read_sprites(game_dir)
    world = data_reader.read_world(game_dir, geometry)
    if geometry:
        geometry.min_x = max(0, geometry.min_x)
        geometry.min_y = max(0, geometry.min_y)
        geometry.max_x = min(world.width - 1, geometry.max_x)
        geometry.max_y = min(world.height - 1, geometry.max_y)

    objects_whitelist = [
        'Kill Area 0',
        'Kill Area 1',
        'Kill Area 2',
        'Fast Travel Sign 0',
    ]

    map_image = renderer.render_world(
        world,
        sprites,
        backgrounds_opacity,
        objects_opacity,
        objects_whitelist,
        tiles_opacity,
        geometry)

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
