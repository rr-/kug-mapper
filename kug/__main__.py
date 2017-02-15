#!/usr/bin/env python3
import os
import re
import random
from typing import Any, Optional, Union, Tuple, List, Dict, Iterator
from PIL import Image, ImageDraw
from kug.util import range2d, progress, scan_tree
from kug.world import World
from kug.world_reader import read_world


ImageObj = Any
Color = Union[Tuple[int, int, int], Tuple[int, int, int, int]]

GAME_DIR = os.path.expanduser(
    '~/.local/share/Steam/steamapps/common/Knytt Underground/World')
SCALE = 4

ROOM_WIDTH = 31
ROOM_HEIGHT = 18
TILE_FULL_WIDTH = 44
TILE_FULL_HEIGHT = 44
TILE_WIDTH = 32
TILE_HEIGHT = 32
TILE_BORDER_WIDTH = (TILE_FULL_WIDTH - TILE_WIDTH) // 2
TILE_BORDER_HEIGHT = (TILE_FULL_HEIGHT - TILE_HEIGHT) // 2
MAX_TILE_X = 5
MAX_TILE_Y = 5
PRETTY_COLORS = False
DEBUG = True


def _read_tile_set_images() -> Dict[str, ImageObj]:
    print('Preparing tile sets...')
    tile_set_images: Dict[str, ImageObj] = {}
    tile_set_images['Null Tileset'] = (
        Image.new(
            mode='RGBA',
            size=(
                MAX_TILE_X * TILE_FULL_WIDTH,
                MAX_TILE_Y * TILE_FULL_HEIGHT),
            color=(255, 0, 0, 255)))
    tile_set_dir = os.path.join(GAME_DIR, 'Tilesets')
    for entry in scan_tree(tile_set_dir):
        name, _ = os.path.splitext(entry.name)
        tile_set_images[name] = (
            Image
            .open(os.path.join(tile_set_dir, entry.path))
            .convert('RGBA'))
    return tile_set_images


def _read_object_images() -> Dict[str, ImageObj]:
    print('Preparing object images...')
    object_images: Dict[str, ImageObj] = {}
    object_dir = os.path.join(GAME_DIR, 'Objects')
    for entry in scan_tree(object_dir):
        name, ext = os.path.splitext(os.path.relpath(entry.path, object_dir))
        if ext == '.ini':
            continue
        object_images[name] = (
            Image
            .open(os.path.join(object_dir, entry.path))
            .convert('RGBA'))
    return object_images


def _create_solid_tile_image(color: Color) -> ImageObj:
    image = Image.new(
        mode='RGBA',
        size=(TILE_FULL_WIDTH, TILE_FULL_HEIGHT),
        color=(color[0], color[1], color[2], 0))
    draw = ImageDraw.Draw(image)
    draw.rectangle(
        (
            TILE_BORDER_WIDTH,
            TILE_BORDER_HEIGHT,
            TILE_BORDER_WIDTH + TILE_WIDTH,
            TILE_BORDER_HEIGHT + TILE_HEIGHT,
        ),
        fill=color)
    return image


def _get_map_coord(
        world_x: int, room_x: int, world_y: int, room_y: int
        ) -> Tuple[int, int]:
    return (
        (world_x * ROOM_WIDTH + room_x) * TILE_WIDTH - TILE_BORDER_WIDTH,
        (world_y * ROOM_HEIGHT + room_y) * TILE_HEIGHT - TILE_BORDER_HEIGHT,
    )


def _to_rgb(color: int) -> Color:
    return (
        color & 0xFF,
        (color >> 8) & 0xFF,
        (color >> 16) & 0xFF)


def _mix_rgb(color1: Color, color2: Color, delta: float) -> Color:
    return tuple(
        int(color1[i] + (color2[i] - color1[i]) * delta)
        for i in range(3))


def _render_backgrounds(map_image: ImageObj, world: World) -> None:
    print('Drawing backgrounds...')
    draw = ImageDraw.Draw(map_image)
    for world_x, world_y in progress(range2d(world.width + 1, world.height + 1)):
        settings = world[world_x, world_y].settings
        color1 = _to_rgb(int(settings['General']['Gradient Top']))
        color2 = _to_rgb(int(settings['General']['Gradient Bottom']))
        for room_y in range(ROOM_HEIGHT * TILE_HEIGHT):
            new_color = _mix_rgb(
                color1, color2, room_y / (ROOM_HEIGHT * TILE_HEIGHT))
            draw.rectangle(
                (
                    world_x * ROOM_WIDTH * TILE_WIDTH,
                    world_y * ROOM_HEIGHT * TILE_HEIGHT + room_y,
                    (world_x + 1) * ROOM_WIDTH * TILE_WIDTH,
                    world_y * ROOM_HEIGHT * TILE_HEIGHT + room_y,
                ),
                fill=new_color)


def _render_tiles(
        map_image: ImageObj,
        world: World,
        tile_set_images: Dict[str, ImageObj]) -> None:
    print('Drawing tiles...')
    black_image = _create_solid_tile_image((0, 0, 0, 255))
    for world_x, world_y in progress(range2d(world.width + 1, world.height + 1)):
        tiles = world[world_x, world_y].tiles
        tile_set_names = [tiles['General']['Tileset %d' % i] for i in range(3)]

        for room_x, room_y in range2d(ROOM_WIDTH, ROOM_HEIGHT):
            tile_str = (
                tiles['Tile Map'][str(room_y)][room_x * 3:room_x * 3 + 3])

            if tile_str[0] == 'X':
                continue

            tile_set_index = int(tile_str[0])
            tile_set_x = int(tile_str[1])
            tile_set_y = int(tile_str[2])
            tile_image = (
                tile_set_images
                .get(
                    tile_set_names[tile_set_index],
                    tile_set_images['Null Tileset'])
                .crop((
                    tile_set_x * TILE_FULL_WIDTH,
                    tile_set_y * TILE_FULL_HEIGHT,
                    (tile_set_x + 1) * TILE_FULL_WIDTH,
                    (tile_set_y + 1) * TILE_FULL_HEIGHT)))

            map_tile_x, map_tile_y = _get_map_coord(
                world_x, room_x, world_y, room_y)

            map_image.paste(
                tile_image if PRETTY_COLORS else black_image,
                (map_tile_x, map_tile_y),
                tile_image)


def _render_tile_modifiers(
        map_image: ImageObj,
        world: World,
        tile_modifier_tiles: Dict[str, ImageObj]) -> None:
    print('Drawing tile modifiers...')
    for world_x, world_y in progress(range2d(world.width + 1, world.height + 1)):
        sprites = world[world_x, world_y].sprites
        tile_modifiers = [
            sprite
            for sprite in sprites.values()
            if 'Sprite' in sprite
            and 'X' in sprite
            and 'Y' in sprite
            and sprite.get('Sprite') in tile_modifier_tiles]
        for room_x, room_y in range2d(ROOM_WIDTH, ROOM_HEIGHT):
            tile_modifier_names = [
                sprite.get('Sprite')
                for sprite in tile_modifiers
                if int(sprite.get('X')) == room_x
                and int(sprite.get('Y')) == room_y]
            if not tile_modifiers:
                continue
            map_tile_x, map_tile_y = _get_map_coord(
                world_x, room_x, world_y, room_y)
            for name in tile_modifier_names:
                map_image.paste(
                    tile_modifier_tiles[name],
                    (map_tile_x, map_tile_y),
                    tile_modifier_tiles[name])


def _render_objects(
        map_image: ImageObj,
        world: World,
        object_tiles: Dict[str, ImageObj],
        whitelist: List[str]) -> None:
    print('Drawing objects...')
    for world_x, world_y in progress(range2d(world.width + 1, world.height + 1)):
        objects = [
            obj
            for obj in world[world_x, world_y].objects.values()
            if 'Object' in obj
            and (whitelist is None or obj['Object'] in whitelist)
            and 'X' in obj
            and 'Y' in obj]
        for obj in objects:
            try:
                map_tile_x, map_tile_y = _get_map_coord(
                    world_x, 0, world_y, 0)
                image_name = world.objects[obj['Object']]['Image']
                object_tile = (
                    object_tiles[image_name]
                    .rotate(int(obj.get('Angle', 0)), expand=True))
                map_image.paste(
                    object_tile,
                    (
                        map_tile_x + int(obj['X']) - object_tile.width // 2,
                        map_tile_y + int(obj['Y']) - object_tile.height // 2,
                    ),
                    object_tile)
            except Exception as ex:
                logging.warning(ex)


def _render_warps(map_image: ImageObj, world: World) -> None:
    print('Drawing warps...')

    overlay_image = Image.new(
        mode='RGBA',
        size=(
            world.width * ROOM_WIDTH * TILE_WIDTH,
            world.height * ROOM_HEIGHT * TILE_HEIGHT))
    draw = ImageDraw.Draw(overlay_image)

    def draw_rectangle(draw, coordinates, outline, width=1):
        for i in range(width):
            rect_start = (coordinates[0] + i, coordinates[1] + i)
            rect_end = (coordinates[2] - i, coordinates[3] - i)
            draw.rectangle((rect_start, rect_end), outline=outline)

    for world_x, world_y in progress(range2d(world.width + 1, world.height + 1)):
        matches = re.findall(
            r'room_set\((\d+),\s*(\d+)\)', world[world_x, world_y].script)

        for match in matches:
            target_x = int(match[0])
            target_y = int(match[1])
            color = tuple([random.randint(100, 200) for _ in range(3)] + [200])

            draw_rectangle(
                draw,
                (
                    world_x * ROOM_WIDTH * TILE_WIDTH,
                    world_y * ROOM_HEIGHT * TILE_HEIGHT,
                    (world_x + 1) * ROOM_WIDTH * TILE_WIDTH,
                    (world_y + 1) * ROOM_HEIGHT * TILE_HEIGHT,
                ),
                outline=color,
                width=16)
            draw_rectangle(
                draw,
                (
                    target_x * ROOM_WIDTH * TILE_WIDTH,
                    target_y * ROOM_HEIGHT * TILE_HEIGHT,
                    (target_x + 1) * ROOM_WIDTH * TILE_WIDTH,
                    (target_y + 1) * ROOM_HEIGHT * TILE_HEIGHT,
                ),
                outline=color,
                width=16)
            draw.line(
                (
                    (world_x + random.uniform(0.3, 0.7)) * ROOM_WIDTH * TILE_WIDTH,
                    (world_y + random.uniform(0.3, 0.7)) * ROOM_HEIGHT * TILE_HEIGHT,
                    (target_x + random.uniform(0.3, 0.7)) * ROOM_WIDTH * TILE_WIDTH,
                    (target_y + random.uniform(0.3, 0.7)) * ROOM_HEIGHT * TILE_HEIGHT,
                ),
                fill=color,
                width=16)

    map_image.paste(overlay_image, (0, 0), overlay_image)


def _create_map_image(world: World) -> ImageObj:
    return Image.new(
        mode='RGB',
        size=(
            world.width * ROOM_WIDTH * TILE_WIDTH,
            world.height * ROOM_HEIGHT * TILE_HEIGHT),
        color=(255, 225, 205))


def main() -> None:
    world = read_world(GAME_DIR, DEBUG)

    print('Reading world data...')
    map_image = _create_map_image(world)
    if PRETTY_COLORS:
        _render_backgrounds(map_image, world)

    object_images = _read_object_images()
    obj_whitelist = [
        'Kill Area 0',
        'Kill Area 1',
        'Kill Area 2',
    ]
    _render_objects(map_image, world, object_images, obj_whitelist)

    tile_set_images = _read_tile_set_images()
    _render_tiles(map_image, world, tile_set_images)

    tile_modifier_tiles = {
        'Tile Modifier 0': _create_solid_tile_image((0, 255, 0, 200)),
        'Tile Modifier 1': _create_solid_tile_image((255, 0, 255, 200)),
        'Tile Modifier 2': _create_solid_tile_image((0, 255, 255, 200)),
    }
    _render_tile_modifiers(map_image, world, tile_modifier_tiles)

    _render_warps(map_image, world)

    print('Rendering PNG...')
    (
        map_image
        .resize((map_image.width // SCALE, map_image.height // SCALE), Image.ANTIALIAS)
        .save('map.png')
    )


if __name__ == '__main__':
    main()