#!/usr/bin/env python3
import os
import argparse
from PIL import Image
from kug import util, data_reader, renderer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    def add_boolean_option(name, dest):
        nonlocal parser
        parser.add_argument(name, dest=dest, action='store_true')
        parser.add_argument(
            name.replace('--', '--no-'), dest=dest, action='store_false')

    parser.add_argument('--game-dir', default=(
        '~/.local/share/Steam/steamapps/common/Knytt Underground/World'))
    parser.add_argument('--output-path', type=str, default='map.png')
    parser.add_argument('--geometry', default='*')
    parser.add_argument('--scale', type=int, default=4)
    add_boolean_option('--render-backgrounds', dest='render_backgrounds')
    add_boolean_option('--render-objects', dest='render_objects')
    add_boolean_option('--mask-tiles', dest='mask_tiles')
    add_boolean_option('--dim', dest='dim')

    parser.set_defaults(
        render_backgrounds=False,
        render_objects=False,
        mask_tiles=True,
        dim=False)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    game_dir: str = os.path.expanduser(args.game_dir)
    geometry: util.Geometry = util.parse_geometry(args.geometry)
    render_backgrounds: bool = args.render_backgrounds
    render_objects: bool = args.render_objects
    mask_tiles: bool = args.mask_tiles
    scale: int = args.scale
    output_path: str = args.output_path
    dim: bool = args.dim

    sprites = data_reader.read_sprites(game_dir)
    world = data_reader.read_world(game_dir, geometry)
    if geometry:
        geometry.min_x = max(0, geometry.min_x)
        geometry.min_y = max(0, geometry.min_y)
        geometry.max_x = min(world.width - 1, geometry.max_x)
        geometry.max_y = min(world.height - 1, geometry.max_y)

    if render_backgrounds:
        if dim:
            backgrounds_opacity = 0.5
        elif render_objects:
            backgrounds_opacity = 1.0
        else:
            backgrounds_opacity = 0.5
    else:
        backgrounds_opacity = 0.0

    if render_objects:
        if dim:
            objects_opacity = 0.3
        else:
            objects_opacity = 1.0
    else:
        objects_opacity = 0.0

    if not mask_tiles:
        if dim:
            tiles_opacity = 0.3
        else:
            tiles_opacity = 1.0
    else:
        tiles_opacity = 0.0

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
