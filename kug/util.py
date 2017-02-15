import os
from progress.bar import Bar
from typing import Iterator, Any, Tuple


def progress(what: Any) -> Any:
    return Bar().iter(list(what))


def range2d(max_x: int, max_y: int) -> Iterator[Tuple[int, int]]:
    for y in range(max_y):
        for x in range(max_x):
            yield (x, y)


def scan_tree(path):
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from scan_tree(entry.path)
        else:
            yield entry
