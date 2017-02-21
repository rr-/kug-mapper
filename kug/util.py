import os
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


def parse_geometry(input: str) -> Optional[Geometry]:
    if not input or input == '*':
        return None
    if ':' in input:
        min_coord, max_coord = input.split(':')
        min_x, min_y = min_coord.split(',')
        max_x, max_y = max_coord.split(',')
    else:
        x, y = input.split(',')
        min_x = max_x = x
        min_y = max_y = y
    return Geometry(int(min_x), int(min_y), int(max_x), int(max_y))


def number_to_spreadsheet_notation(num: int) -> str:
    title = ''
    alphabet = string.ascii_uppercase
    while num:
        mod = (num - 1) % 26
        num = (num - mod) // 26
        title += alphabet[mod]
    return title[::-1]
