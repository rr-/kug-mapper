import os
import sys
import io
import re
import math
import random
from typing import Any, Optional, Union, Tuple, Set, List, Dict
from PIL import Image, ImageFont, ImageDraw, ImageMath
from kug import data, util


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

SPRITE_DEFINITIONS = {
    'Tile Modifier 0': ((0, 255, 0, 200), -6, -6, 1),  # secret passage
    'Tile Modifier 1': ((255, 0, 255, 200), -6, -6, 1),  # earthquake
    'Tile Modifier 2': ((0, 255, 255, 200), -6, -6, 1),  # ?

    'NPC 0': (283, 0, 0, 1),
    'NPC 1': (283, 0, 0, 1),
    'NPC 2': (283, 0, 0, 1),
    'NPC 3': (283, 0, 0, 1),
    'NPC 4': (283, 0, 0, 1),
    'NPC 5': (283, 0, 0, 1),
    'NPC 6': (283, 0, 0, 1),
    'NPC 7': (283, 0, 0, 1),
    'NPC 8': (283, 0, 0, 1),
    'NPC 9': (283, 0, 0, 1),
    'NPC 10': (283, 0, 0, 1),
    'NPC 11': (283, 0, 0, 1),
    'NPC 12': (283, 0, 0, 1),
    'NPC 13': (283, 0, 0, 1),
    'NPC 14': (283, 0, 0, 1),
    'NPC 15': (283, 0, 0, 1),
    'NPC 16': (283, 0, 0, 1),
    'NPC 17': (283, 0, 0, 1),
    'NPC 18': (283, 0, 0, 1),
    'NPC 19': (283, 0, 0, 1),
    'NPC 20': (283, 0, 0, 1),
    'NPC 21': (283, 0, 0, 1),
    'NPC 22': (283, 0, 0, 1),
    'NPC 23': (283, 0, 0, 1),
    'NPC 24': (283, 0, 0, 1),
    'NPC 25': (283, 0, 0, 1),
    'NPC 26': (283, 0, 0, 1),
    'NPC 27': (283, 0, 0, 1),
    'NPC 28': (283, 0, 0, 1),
    'NPC 29': (283, 0, 0, 1),
    'NPC 30': (283, 0, 0, 1),
    'NPC 31': (283, 0, 0, 1),
    'NPC 32': (283, 0, 0, 1),
    'NPC 33': (283, 0, 0, 1),
    'NPC 34': (283, 0, 0, 1),
    'NPC 35': (283, 0, 0, 1),
    'NPC 36': (283, 0, 0, 1),
    'NPC 37': (283, 0, 0, 1),
    'NPC 38': (283, 0, 0, 1),
    'NPC 39': (283, 0, 0, 1),
    'NPC 40': (283, 0, 0, 1),
    'NPC 41': (283, 0, 0, 1),
    'NPC 42': (283, 0, 0, 1),
    'NPC 43': (283, 0, 0, 1),
    'NPC 44': (283, 0, 0, 1),
    'NPC 45': (283, 0, 0, 1),
    'NPC 46': (283, 0, 0, 1),
    'NPC 47': (283, 0, 0, 1),
    'NPC 48': (283, 0, 0, 1),
    'NPC 49': (283, 0, 0, 1),
    'NPC 50': (283, 0, 0, 1),
    'NPC 51': (283, 0, 0, 1),
    'NPC 52': (283, 0, 0, 1),
    'NPC 53': (283, 0, 0, 1),
    'NPC 54': (283, 0, 0, 1),
    'NPC 55': (283, 0, 0, 1),
    'NPC 56': (283, 0, 0, 1),
    'NPC 57': (283, 0, 0, 1),
    'NPC 58': (283, 0, 0, 1),
    'NPC 59': (283, 0, 0, 1),
    'NPC 60': (283, 0, 0, 1),
    'NPC 61': (283, 0, 0, 1),
    'NPC 62': (283, 0, 0, 1),
    'NPC 63': (283, 0, 0, 1),
    'NPC 64': (283, 0, 0, 1),
    'NPC 65': (283, 0, 0, 1),
    'NPC 66': (283, 0, 0, 1),
    'NPC 67': (283, 0, 0, 1),
    'NPC 68': (283, 0, 0, 1),
    'NPC 69': (283, 0, 0, 1),

    'Orb 0': (296, 0, 0, 1),  # red orb
    'Orb 1': (290, 0, 0, 1),  # green orb
    'Orb 2': (295, 0, 0, 1),  # blue orb
    'Orb 3': (892, 0, 0, 1),  # white orb
    'Orb 4': (2606, 0, 0, 1),  # yellow orb
    'Orb 5': (2084, 0, 0, 1),  # pink orb

    'Bouncy Ring 0': (1417, 0, 0, 1),
    'Bell 0': (1151, 0, 0, 0),
    'Warp Symbol 0': (11964, 0, 0, 1), # warp scribblings (twilight zone)
    'Warp Symbol 1': (11964, 0, 0, 1), # warp scribblings (outside world)
    'Save Point 0': (178, 0, -16, 1),

    'Green Switch 0': (1400, 0, 0, 1), # green block button
    'Time Block 0': (706, 0, 0, 1),  # green block, standard variant
    'Time Block 1': (706, 0, 0, 1),  # green block, rare variant

    'Blue Switch 0': (1109, 0, 0, 1),  # blue block button
    'Switch Block 0': (1143, 0, 0, 1), # blue block

    'Red Switch 0': (887, 0, 0, 1),  # red block button
    'Switch Block 1': (1140, 0, 0, 1), # red block

    'Grey Switch 0': (1403, 0, 20, 1), # grey door button
    'Door 0': (1404, -12, -32, 1),  # grey door
    'Door 1': (1600, -12, -32, 1),  # red door
    'Door 2': (2062, -12, -32, 1),  # green door
    'Door 3': (1601, -12, -32, 1),  # bell door

    'Lava 0': (18160, 0, 2, 0),  # horizontal lava, upper layer
    'Lava 1': (23065, -6, -6, 0),  # horizontal lava, lower layer
    'Lava 2': (18370, 8, 0, 0),  # lava pillar
    'Lava 3': (18379, 0, 0, 0),  # lava pillar end
    'Lava 4': (18478, 0, 0, 0),  # lava pillar start (from left)
    'Lava 5': (18572, 0, 0, 0),  # lava pillar start (from right)

    'Slime 0': (3251, 0, 2, 0),  # horizontal slime, upper layer
    'Slime 1': (23061, -6, -6, 0),  # horizontal slime, lower layer
    'Slime 2': (3861, -8, 0, 0),  # slime pillar
    'Slime 3': (3722, 0, 0, 0),  # horizontal slime corner, \
    'Slime 4': (3738, 0, 0, 0),  # horizontal slime corner, /
    'Slime 5': (3589, 0, 0, 0),  # slime fountain
}


def _parse_float(x: Any) -> Optional[float]:
    try:
        return float(re.sub(r'[^\d\.]', '', str(x).replace(',', '.')))
    except ValueError:
        return None


def _get_room_name_x(x: int) -> str:
    return util.number_to_spreadsheet_notation(x + 1)


def _get_room_name_y(y: int) -> str:
    return str(y + 1)


def _get_room_name(x: int, y: int) -> str:
    return _get_room_name_x(x) + _get_room_name_y(y)


@util.memoize
def _read_tile_set_image(game_dir: str, name: str) -> ImageObj:
    tile_set_path = os.path.join(game_dir, 'Tilesets', name + '.png')
    if os.path.exists(tile_set_path):
        return (
            Image
            .open(os.path.join(tile_set_path, tile_set_path))
            .convert('RGBA'))

    return Image.new(
        mode='RGBA',
        size=(
            MAX_TILE_X * TILE_FULL_WIDTH,
            MAX_TILE_Y * TILE_FULL_HEIGHT),
        color=(255, 0, 0, 255))


@util.memoize
def _read_tile_image(game_dir: str, name: str, x: int, y: int) -> ImageObj:
    return (
        _read_tile_set_image(game_dir, name)
        .crop((
            x * TILE_FULL_WIDTH,
            y * TILE_FULL_HEIGHT,
            (x + 1) * TILE_FULL_WIDTH,
            (y + 1) * TILE_FULL_HEIGHT)))


@util.memoize
def _read_object_image(game_dir: str, name: str) -> ImageObj:
    object_path = os.path.join(game_dir, 'Objects', name + '.png')
    return Image.open(object_path).convert('RGBA')


@util.memoize
def _create_sprite_image(
        sprites: data.SpriteArchive,
        sprite_id: Union[int, Color]) -> ImageObj:
    if type(sprite_id) is int:
        content = sprites.read(sprite_id)
        return Image.open(io.BytesIO(content)).convert('RGBA')
    else:
        return _create_solid_tile_image(sprite_id)


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


def _render_backgrounds(
        room_image: ImageObj,
        room_data: data.Room,
        opacity: float) -> None:
    color1 = _to_rgb(int(room_data.settings['General']['Gradient Top']))
    color2 = _to_rgb(int(room_data.settings['General']['Gradient Bottom']))
    draw = ImageDraw.Draw(room_image)
    for room_y in range(ROOM_HEIGHT * TILE_HEIGHT):
        new_color = _mix_rgb(
            color1, color2, room_y / (ROOM_HEIGHT * TILE_HEIGHT))
        new_color = _mix_rgb(DEFAULT_BACKGROUND, new_color, opacity)
        draw.rectangle(
            (0, room_y, room_image.width, room_y),
            fill=new_color)


def _render_tiles(
        room_image: ImageObj,
        room_data: data.Room,
        tiles_opacity: float) -> None:
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
            _read_tile_image(
                room_data.world.game_dir,
                tile_set_names[tile_set_index],
                tile_set_x,
                tile_set_y))

        room_image.paste(
            tile_image,
            (
                room_x * TILE_WIDTH - TILE_BORDER_WIDTH,
                room_y * TILE_HEIGHT - TILE_BORDER_HEIGHT,
            ),
            tile_image)
        room_image.paste(
            black_image,
            (
                room_x * TILE_WIDTH - TILE_BORDER_WIDTH,
                room_y * TILE_HEIGHT - TILE_BORDER_HEIGHT,
            ),
            Image.merge(
                'RGBA',
                [
                    ImageMath.eval(
                        'convert(convert(image, "F") * coeff, "L")',
                        image=band,
                        coeff=tiles_opacity)
                    for i, band in enumerate(tile_image.split())
                ]))


def _render_sprites(
        room_image: ImageObj,
        room_data: data.Room,
        sprites: data.SpriteArchive,
        layer_to_draw: int) -> None:
    for room_x, room_y in util.range2d(ROOM_WIDTH, ROOM_HEIGHT):
        for sprite_id, offset_x, offset_y, layer in [
                SPRITE_DEFINITIONS[sprite['Sprite']]
                for key, sprite in room_data.sprites.items()
                if key != 'Null Sprite'
                and 'Sprite' in sprite
                and 'X' in sprite
                and 'Y' in sprite
                and sprite['Sprite'] in SPRITE_DEFINITIONS
                and int(sprite['X']) == room_x
                and int(sprite['Y']) == room_y]:
            if layer != layer_to_draw:
                continue
            sprite_image = _create_sprite_image(sprites, sprite_id)
            room_image.paste(
                sprite_image,
                (
                    room_x * TILE_WIDTH + offset_x,
                    room_y * TILE_HEIGHT + offset_y,
                ),
                sprite_image)


def _render_objects(
        room_image: ImageObj,
        room_data: data.Room,
        world: data.World,
        objects_opacity: float,
        objects_whitelist: List[str],
        layers: Any) -> None:

    def get_layer(object):
        try:
            default = 0
            ret = None
            if 'Layer Override' in object:
                ret = _parse_float(object['Layer Override'])
            if (ret is None
                    and 'Object' in object
                    and object['Object'] in world.objects):
                ret = _parse_float(world.objects[object['Object']].get('Layer'))
            return ret or default
        except:
            return default

    objects = [
        obj
        for obj in room_data.objects.values()
        if 'Object' in obj
        and obj['Object'] in world.objects
        and (objects_whitelist is None or obj['Object'] in objects_whitelist)
        and 'X' in obj
        and 'Y' in obj]
    objects = sorted(objects, key=get_layer)

    for obj in objects:
        world_obj = world.objects[obj['Object']]
        image_name = world_obj['Image']
        layer = get_layer(obj)
        if 'Scale Multiplier' in obj:
            scale = _parse_float(obj['Scale Multiplier']) or 1
        elif 'Scale Min' in world_obj:
            scale = _parse_float(world_obj['Scale Min']) / 100.0 or 1
        angle = _parse_float(obj.get('Angle')) or 0
        if 'Transparency Override' in obj:
            alpha = 255 - (_parse_float(obj['Transparency Override']) or 0)
        elif 'Transparency Max' in world_obj:
            alpha = 255 - (_parse_float(world_obj['Transparency Max']) or 0)
        else:
            alpha = 255
        alpha *= objects_opacity
        coeff = int(obj.get('RGB Coefficient', 0xFFFFFF))
        flip = bool(obj.get('Flip', False))
        color = (*_to_rgb(coeff), alpha)

        if layer not in layers:
            continue

        object_tile = _read_object_image(
            room_data.world.game_dir, image_name)
        object_tile = Image.merge(
            'RGBA',
            [
                ImageMath.eval(
                    'convert(convert(image, "F") * coeff, "L")',
                    image=band,
                    coeff=color[i] / 255.)
                for i, band in enumerate(object_tile.split())
            ])
        object_tile = object_tile.resize(
            (
                int(object_tile.width * scale),
                int(object_tile.height * scale),
            ))
        if flip:
            object_tile = object_tile.transpose(Image.FLIP_LEFT_RIGHT)
        object_tile = object_tile.rotate(angle, expand=True)

        x0 = _parse_float(obj['X']) or 0
        y0 = _parse_float(obj['Y']) or 0
        x1 = x0 - object_tile.width / 2
        y1 = y0 - object_tile.height / 2
        hx = _parse_float(world.objects[obj['Object']].get('X Hotspot')) or 0
        hy = _parse_float(world.objects[obj['Object']].get('Y Hotspot')) or 0
        hotspot_theta = math.atan2(hy, hx) - math.radians(angle)
        hotspot_delta = math.sqrt(hx * hx + hy * hy)
        x2 = x1 - hotspot_delta * math.cos(hotspot_theta)
        y2 = y1 - hotspot_delta * math.sin(hotspot_theta)
        room_image.paste(object_tile, (int(x2), int(y2)), object_tile)


def _render_warps(
        room_image: ImageObj,
        room_data: data.Room,
        outgoing_warps: WarpDict,
        incoming_warps: WarpDict) -> None:
    draw = ImageDraw.Draw(room_image)
    font = ImageFont.truetype(FONT_NAME, FONT_SIZE)

    for i, source_pos in enumerate(incoming_warps.get(room_data.pos, [])):
        source_x, source_y = source_pos
        draw.text(
            (10, 10 + FONT_SIZE * i),
            _get_room_name(source_x, source_y) + '\N{RIGHTWARDS ARROW}',
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


def _render_room_name(room_image: ImageObj, room_data: data.Room) -> None:
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


def _get_warp_data(world: data.World) -> Tuple[WarpDict, WarpDict]:
    regex = r'room_set\((\d+),\s*(\d+)\)'
    outgoing_warps: WarpDict = {}
    incoming_warps: WarpDict = {}
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


def _report_unknown_sprites(
        known_names: Set[str], all_names: Set[str]) -> None:
    for name in sorted(all_names):
        if name not in known_names:
            print('Skipped sprite %s' % name, file=sys.stderr)


def render_world(
        world: data.World,
        sprites: data.SpriteArchive,
        backgrounds_opacity: float,
        objects_opacity: float,
        objects_whitelist: List[str],
        tiles_opacity: float,
        geometry: Optional[util.Geometry]):
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

        if backgrounds_opacity:
            _render_backgrounds(room_image, room_data, backgrounds_opacity)
        _render_objects(
            room_image, room_data, world, objects_opacity, None, range(0, 7))
        _render_sprites(room_image, room_data, sprites, 0)
        _render_tiles(room_image, room_data, tiles_opacity)
        _render_objects(
            room_image, room_data, world, objects_opacity, None, range(7, 999))
        _render_objects(
            room_image, room_data, world, 1.0, objects_whitelist, range(999))
        _render_sprites(room_image, room_data, sprites, 1)
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

    _report_unknown_sprites(
        set(SPRITE_DEFINITIONS.keys()),
        set([
            sprite['Sprite']
            for room in world
            if room.sprites
            for sprite in room.sprites.values()
            if 'X' in sprite
            and 'Y' in sprite
            and 'Sprite' in sprite
        ]))

    return map_image
