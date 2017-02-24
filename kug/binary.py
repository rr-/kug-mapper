import io
import struct


def read_u8(handle: io.BufferedReader) -> int:
    return struct.unpack('B', handle.read(1))[0]


def read_u32(handle: io.BufferedReader) -> int:
    return struct.unpack('<L', handle.read(4))[0]


def read_zero_string(handle: io.BufferedReader) -> str:
    ret = b''
    while True:
        byte = read_u8(handle)
        if byte == 0:
            break
        ret += bytes([byte])
    return ret.decode('utf-8')


