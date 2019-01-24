import io
import struct
import typing as T


def read_u8(handle: T.BinaryIO) -> int:
    return T.cast(int, struct.unpack("B", handle.read(1))[0])


def read_u32(handle: T.BinaryIO) -> int:
    return T.cast(int, struct.unpack("<L", handle.read(4))[0])


def read_zero_string(handle: T.BinaryIO) -> str:
    ret = b""
    while True:
        byte = read_u8(handle)
        if byte == 0:
            break
        ret += bytes([byte])
    return ret.decode("utf-8")
