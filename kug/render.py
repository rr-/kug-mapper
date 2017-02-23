import os
import re
import random
from string import ascii_lowercase
from typing import Any, Optional, Union, Tuple, List, Dict
from PIL import Image, ImageFont, ImageDraw
from kug import util
from kug.util import Geometry
from kug.world import World, RoomData


ImageObj = Any
Color = Union[Tuple[int, int, int], Tuple[int, int, int, int]]
Coord = Tuple[int, int]
WarpDict = Dict[Coord, List[Coord]]

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
FONT_SIZE = 50
FONT_NAME = 'DejaVuSansMono.ttf'

OUTGOING_WARP_FONT_COLOR = 'red'
INCOMING_WARP_FONT_COLOR = 'magenta'
ROOM_BORDER_COLOR = 'brown'
ROOM_BORDER_COLOR = 'grey'
ROOM_BORDER_SIZE = 4
AXIS_SIZE_X = 120
AXIS_SIZE_Y = 80
AXIS_COLOR = 'black'
AXIS_FONT_COLOR = 'white'
ROOM_NAME_FONT_COLOR = (128, 128, 128, 128)
DEFAULT_BACKGROUND = (255, 225, 205)


def _get_room_name_x(x: int) -> str:
    return util.number_to_spreadsheet_notation(x + 1)


def _get_room_name_y(y: int) -> str:
    return str(y + 1)


def _get_room_name(x: int, y: int) -> str:
    return _get_room_name_x(x) + _get_room_name_y(y)


def _read_tile_set_images(game_dir: str) -> Dict[str, ImageObj]:
    tile_set_images: Dict[str, ImageObj] = {}
    tile_set_images['Null Tileset'] = (
        Image.new(
            mode='RGBA',
            size=(
                MAX_TILE_X * TILE_FULL_WIDTH,
                MAX_TILE_Y * TILE_FULL_HEIGHT),
            color=(255, 0, 0, 255)))
    tile_set_dir = os.path.join(game_dir, 'Tilesets')
    for entry in util.scan_tree(tile_set_dir):
        name, _ = os.path.splitext(entry.name)
        tile_set_images[name] = (
            Image
            .open(os.path.join(tile_set_dir, entry.path))
            .convert('RGBA'))
    return tile_set_images


def _read_object_images(game_dir: str) -> Dict[str, ImageObj]:
    object_images: Dict[str, ImageObj] = {}
    object_dir = os.path.join(game_dir, 'Objects')
    for entry in util.scan_tree(object_dir):
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


def _to_rgb(color: int) -> Color:
    return (
        color & 0xFF,
        (color >> 8) & 0xFF,
        (color >> 16) & 0xFF)


def _mix_rgb(color1: Color, color2: Color, delta: float) -> Color:
    return tuple(
        int(color1[i] + (color2[i] - color1[i]) * delta)
        for i in range(3))


def _render_backgrounds(room_image: ImageObj, room_data: RoomData) -> None:
    color1 = _to_rgb(int(room_data.settings['General']['Gradient Top']))
    color2 = _to_rgb(int(room_data.settings['General']['Gradient Bottom']))
    draw = ImageDraw.Draw(room_image)
    for room_y in range(ROOM_HEIGHT * TILE_HEIGHT):
        new_color = _mix_rgb(
            color1, color2, room_y / (ROOM_HEIGHT * TILE_HEIGHT))
        new_color = _mix_rgb(DEFAULT_BACKGROUND, new_color, 0.5)
        draw.rectangle(
            (0, room_y, room_image.width, room_y),
            fill=new_color)


def _render_tiles(
        room_image: ImageObj,
        room_data: RoomData,
        tile_set_images: Dict[str, ImageObj],
        mask_tiles: bool) -> None:
    black_image = _create_solid_tile_image((0, 0, 0, 255))
    tile_set_names = [
        room_data.tiles['General']['Tileset %d' % i] for i in range(3)]

    for room_x, room_y in util.range2d(ROOM_WIDTH, ROOM_HEIGHT):
        tile_str = (
            room_data.tiles
            ['Tile Map']
            [str(room_y)]
            [room_x * 3:room_x * 3 + 3])

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

        room_image.paste(
            black_image if mask_tiles else tile_image,
            (
                room_x * TILE_WIDTH - TILE_BORDER_WIDTH,
                room_y * TILE_HEIGHT - TILE_BORDER_HEIGHT,
            ),
            tile_image)


def _render_tile_modifiers(
        room_image: ImageObj,
        room_data: RoomData,
        tile_modifier_tiles: Dict[str, ImageObj]) -> None:
    tile_modifiers = [
        sprite
        for sprite in room_data.sprites.values()
        if 'Sprite' in sprite
        and 'X' in sprite
        and 'Y' in sprite
        and sprite.get('Sprite') in tile_modifier_tiles]
    for room_x, room_y in util.range2d(ROOM_WIDTH, ROOM_HEIGHT):
        tile_modifier_names = [
            sprite.get('Sprite')
            for sprite in tile_modifiers
            if int(sprite.get('X')) == room_x
            and int(sprite.get('Y')) == room_y]
        if not tile_modifiers:
            continue
        for name in set(tile_modifier_names):
            room_image.paste(
                tile_modifier_tiles[name],
                (
                    room_x * TILE_WIDTH - TILE_BORDER_WIDTH,
                    room_y * TILE_HEIGHT - TILE_BORDER_HEIGHT,
                ),
                tile_modifier_tiles[name])


def _render_objects(
        room_image: ImageObj,
        room_data: RoomData,
        world: World,
        object_tiles: Dict[str, ImageObj],
        whitelist: List[str]) -> None:
    objects = [
        obj
        for obj in room_data.objects.values()
        if 'Object' in obj
        and (whitelist is None or obj['Object'] in whitelist)
        and 'X' in obj
        and 'Y' in obj]
    for obj in objects:
        try:
            image_name = world.objects[obj['Object']]['Image']
            object_tile = (
                object_tiles[image_name]
                .rotate(int(obj.get('Angle', 0)), expand=True))
            room_image.paste(
                object_tile,
                (
                    int(obj['X']) - object_tile.width // 2,
                    int(obj['Y']) - object_tile.height // 2,
                ),
                object_tile)
        except Exception as ex:
            print(ex, file=os.sys.stderr)


def _render_warps(
        room_image: ImageObj,
        room_data: RoomData,
        outgoing_warps: WarpDict,
        incoming_warps: WarpDict) -> None:
    draw = ImageDraw.Draw(room_image)
    font = ImageFont.truetype(FONT_NAME, FONT_SIZE)

    for i, source_pos in enumerate(incoming_warps.get(room_data.pos, [])):
        source_x, source_y = source_pos
        draw.text(
            (10, 10 + FONT_SIZE * i),
            _get_room_name(source_x, source_y) + '\N{RIGHTWARDS ARROW}' ,
            font=font,
            fill=INCOMING_WARP_FONT_COLOR)

    for i, target_pos in enumerate(outgoing_warps.get(room_data.pos, [])):
        target_x, target_y = target_pos
        text = '\N{RIGHTWARDS ARROW}' + _get_room_name(target_x, target_y)
        text_width, _ = font.getsize(text)
        draw.text(
            (room_image.width - 10 - text_width, 10 + FONT_SIZE * i),
            text,
            font=font,
            fill=OUTGOING_WARP_FONT_COLOR)


def _render_room_name(room_image: ImageObj, room_data: RoomData) -> None:
    overlay_image = Image.new(size=room_image.size, mode='RGBA')
    draw = ImageDraw.Draw(overlay_image)
    font = ImageFont.truetype(FONT_NAME, FONT_SIZE)
    text = _get_room_name(room_data.x, room_data.y)
    text_width, text_height = font.getsize(text)
    draw.text(
        (
            (room_image.width - text_width) / 2,
            10,
        ),
        text,
        font=font,
        fill=ROOM_NAME_FONT_COLOR)
    room_image.paste(overlay_image, (0, 0), overlay_image)


def _render_axes(geometry: util.Geometry, map_image: ImageObj) -> None:
    draw = ImageDraw.Draw(map_image)
    font = ImageFont.truetype(FONT_NAME, FONT_SIZE)

    for world_x in range(geometry.min_x, geometry.max_x + 1):
        text = _get_room_name_x(world_x)
        text_width, text_height = font.getsize(text)
        x1 = (
            AXIS_SIZE_X + ROOM_BORDER_SIZE
            + (world_x - geometry.min_x)
            * (ROOM_WIDTH * TILE_WIDTH + ROOM_BORDER_SIZE))
        x2 = x1 + ROOM_WIDTH * TILE_WIDTH - 1
        y1 = 0
        y2 = AXIS_SIZE_Y - 1

        draw.rectangle((x1, y1, x2, y2), fill=AXIS_COLOR)
        draw.text(
            (
                x1 + (x2 - x1 - text_width) / 2,
                y1 + (y2 - y1 - text_height) / 2,
            ),
            text,
            font=font,
            fill=AXIS_FONT_COLOR)

    for world_y in range(geometry.min_y, geometry.max_y + 1):
        text = _get_room_name_y(world_y)
        text_width, text_height = font.getsize(text)
        x1 = 0
        x2 = AXIS_SIZE_X - 1
        y1 = (
            AXIS_SIZE_Y + ROOM_BORDER_SIZE
            + (world_y - geometry.min_y)
            * (ROOM_HEIGHT * TILE_HEIGHT + ROOM_BORDER_SIZE))
        y2 = y1 + ROOM_HEIGHT * TILE_HEIGHT - 1

        draw.rectangle((x1, y1, x2, y2), fill=AXIS_COLOR)
        draw.text(
            (
                x1 + (x2 - x1 - text_width) / 2,
                y1 + (y2 - y1 - text_height) / 2,
            ),
            text,
            font=font)

    draw.rectangle((0, 0, AXIS_SIZE_X - 1, AXIS_SIZE_Y - 1), fill=AXIS_COLOR)

def _create_map_image(geometry: util.Geometry) -> ImageObj:
    width = geometry.max_x + 1 - geometry.min_x
    height = geometry.max_y + 1 - geometry.min_y
    return Image.new(
        mode='RGB',
        size=(
            AXIS_SIZE_X + ROOM_BORDER_SIZE
            + width * ((ROOM_WIDTH * TILE_WIDTH) + ROOM_BORDER_SIZE),
            AXIS_SIZE_Y + ROOM_BORDER_SIZE
            + height * ((ROOM_HEIGHT * TILE_HEIGHT) + ROOM_BORDER_SIZE),
        ),
        color=ROOM_BORDER_COLOR)


def _create_room_image() -> ImageObj:
    return Image.new(
        mode='RGB',
        size=(ROOM_WIDTH * TILE_WIDTH, ROOM_HEIGHT * TILE_HEIGHT),
        color=DEFAULT_BACKGROUND)


def _get_warp_data(world: World) -> Tuple[WarpDict, WarpDict]:
    regex = r'room_set\((\d+),\s*(\d+)\)'
    outgoing_warps: WarpData = {}
    incoming_warps: WarpData = {}
    for world_x, world_y in util.range2d(
            0, 0, world.width + 1, world.height + 1):
        for match in re.findall(regex, world[world_x, world_y].script or ''):
            target_x = int(match[0])
            target_y = int(match[1])

            if not (world_x, world_y) in outgoing_warps:
                outgoing_warps[world_x, world_y] = []
            outgoing_warps[world_x, world_y].append((target_x, target_y))

            if not (target_x, target_y) in incoming_warps:
                incoming_warps[target_x, target_y] = []
            incoming_warps[target_x, target_y].append((world_x, world_y))
    return outgoing_warps, incoming_warps


def render_world(
        world: World,
        render_backgrounds: bool,
        mask_tiles: bool,
        geometry: Optional[util.Geometry]):
    tile_set_images = _read_tile_set_images(world.game_dir)
    object_images = _read_object_images(world.game_dir)

    tile_modifier_tiles = {
        'Tile Modifier 0': _create_solid_tile_image((0, 255, 0, 200)),
        'Tile Modifier 1': _create_solid_tile_image((255, 0, 255, 200)),
        'Tile Modifier 2': _create_solid_tile_image((0, 255, 255, 200)),
    }
    obj_whitelist = [
        'Kill Area 0',
        'Kill Area 1',
        'Kill Area 2',
    ]

    if not geometry:
        geometry = util.Geometry(0, 0, world.width - 1, world.height - 1)

    map_image = _create_map_image(geometry)
    outgoing_warps, incoming_warps = _get_warp_data(world)
    for world_x, world_y in util.progress(
            util.range2d(
                geometry.min_x,
                geometry.min_y,
                geometry.max_x + 1,
                geometry.max_y + 1)):
        room_image = _create_room_image()
        room_data = world[world_x, world_y]

        if render_backgrounds:
            _render_backgrounds(room_image, room_data)
        _render_objects(
            room_image,
            room_data,
            world,
            object_images,
            obj_whitelist)
        _render_tiles(room_image, room_data, tile_set_images, mask_tiles)
        _render_tile_modifiers(
            room_image, room_data, tile_modifier_tiles)
        _render_warps(room_image, room_data, outgoing_warps, incoming_warps)
        _render_room_name(room_image, room_data)

        map_image.paste(
            room_image,
            (
                AXIS_SIZE_X + ROOM_BORDER_SIZE
                + (world_x - geometry.min_x)
                * (room_image.width + ROOM_BORDER_SIZE),
                AXIS_SIZE_Y + ROOM_BORDER_SIZE
                + (world_y - geometry.min_y)
                * (room_image.height + ROOM_BORDER_SIZE)
            ))

    _render_axes(geometry, map_image)
    return map_image
