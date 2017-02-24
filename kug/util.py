import os
import re
import string
from progress.bar import Bar
from typing import Iterator, Optional, Any, Tuple, List


class Geometry:
    min_x: int
    max_y: int
    min_x: int
    max_y: int

    def __init__(self, min_x: int, min_y: int, max_x: int, max_y: int) -> None:
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y


def progress(what: Any) -> Any:
    return Bar().iter(list(what))


def range2d(*args: int) -> Iterator[Tuple[int, int]]:
    if len(args) == 2:
        min_x = min_y = 0
        max_x, max_y = args
    elif len(args) == 4:
        min_x, min_y, max_x, max_y = args
    for y in range(min_y, max_y):
        for x in range(min_x, max_x):
            yield (x, y)


def scan_tree(path):
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from scan_tree(entry.path)
        else:
            yield entry


def parse_coord(input: str) -> Tuple[int, int]:
    match = re.match('(\d+),(\d+)', input)
    if match:
        return int(match.group(1)), int(match.group(2))
    match = re.match('([a-zA-Z]+)(\d+)', input)
    if match:
        return (
            spreadsheet_notation_to_number(match.group(1)) - 1,
            int(match.group(2)) - 1)
    raise ValueError('Invalid coordinate')


def parse_geometry(input: str) -> Optional[Geometry]:
    if not input or input == '*':
        return None
    if ':' in input:
        min_coord, max_coord = input.split(':')
        min_x, min_y = parse_coord(min_coord)
        max_x, max_y = parse_coord(max_coord)
        return Geometry(min_x, min_y, max_x, max_y)
    else:
        x, y = parse_coord(input)
        return Geometry(x, y, x, y)


def number_to_spreadsheet_notation(num: int) -> str:
    ret = ''
    alphabet = string.ascii_uppercase
    while num:
        mod = (num - 1) % 26
        num = (num - mod) // 26
        ret += alphabet[mod]
    return ret[::-1]


def spreadsheet_notation_to_number(input: str) -> int:
    ret = 0
    alphabet = string.ascii_uppercase
    while input:
        ret *= 26
        ret += alphabet.index(input[0]) + 1
        input = input[1:]
    return ret


def memoize(f):
    results = {}
    def helper(*args):
        if args not in results:
            results[args] = f(*args)
        return results[args]
    return helper
