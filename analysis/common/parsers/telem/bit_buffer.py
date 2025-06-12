from dataclasses import dataclass
from typing import Optional
import math

@dataclass
class TelemBitBufferHandle:
    offset: int  # bit offset
    size: int    # bit size

class TelemBitBuffer:
    """
    A Python reimplementation of the C++ BitBuffer, with optional existing buffer injection.
    """
    __offset_hack = 1  # mimic C++ internal offset hack if needed

    def __init__(self, bit_size: int, buffer: Optional[bytearray] = None):
        self._bit_size = bit_size
        byte_count = (bit_size + 7) >> 3
        byte_count += TelemBitBuffer.__offset_hack
        if buffer is not None:
            if len(buffer) < byte_count:
                raise ValueError(f"Provided buffer too small: need {byte_count}, got {len(buffer)}")
            self._buffer = buffer
        else:
            self._buffer = bytearray(byte_count)

    def bit_size(self) -> int:
        return self._bit_size

    def write(self, handle: TelemBitBufferHandle, data: bytes) -> None:
        """
        Write bits from 'data' (bytes, length = ceil(handle.size/8)) into the buffer at the specified handle.
        """
        if handle.offset + handle.size > self._bit_size:
            raise ValueError("Cannot write: not enough space in buffer.")

        byte_offset = (handle.offset >> 3) + TelemBitBuffer.__offset_hack
        bit_offset = handle.offset & 7
        total_bits = handle.size
        bit_index = 0

        # fast path: aligned to byte
        if bit_offset == 0:
            whole_bytes = total_bits >> 3
            self._buffer[byte_offset:byte_offset+whole_bytes] = data[:whole_bytes]
            bit_index = whole_bytes * 8

        # copy remaining bits
        while bit_index < total_bits:
            dst_byte_index = byte_offset + (bit_index >> 3)
            dst_bit_pos = (bit_index + bit_offset) & 7
            src_byte_index = bit_index >> 3
            src_bit_mask = (data[src_byte_index] >> (bit_index & 7)) & 1
            # clear then set
            self._buffer[dst_byte_index] &= ~(1 << dst_bit_pos)
            self._buffer[dst_byte_index] |= (src_bit_mask << dst_bit_pos)
            bit_index += 1

    def read(self, handle: TelemBitBufferHandle) -> Optional[bytes]:
        """
        Read bits as bytes from the buffer. Returns bytes object of length ceil(size/8), or None if out of range.
        """
        if handle.offset + handle.size > self._bit_size or handle.size == 0:
            return None

        byte_offset = (handle.offset >> 3) + TelemBitBuffer.__offset_hack
        bit_offset = handle.offset & 7
        total_bits = handle.size
        out_len = (total_bits + 7) >> 3
        out = bytearray(out_len)
        bit_index = 0

        # fast path: aligned to byte
        if bit_offset == 0:
            whole_bytes = total_bits >> 3
            out[:whole_bytes] = self._buffer[byte_offset:byte_offset+whole_bytes]
            bit_index = whole_bytes * 8

        # copy remaining bits
        while bit_index < total_bits:
            dst_byte_index = bit_index >> 3
            dst_bit_pos = bit_index & 7
            src_byte_index = byte_offset + ((bit_index + bit_offset) >> 3)
            src_bit_pos = (bit_index + bit_offset) & 7
            bit_val = (self._buffer[src_byte_index] >> src_bit_pos) & 1
            out[dst_byte_index] &= ~(1 << dst_bit_pos)
            out[dst_byte_index] |= (bit_val << dst_bit_pos)
            bit_index += 1

        return bytes(out)
