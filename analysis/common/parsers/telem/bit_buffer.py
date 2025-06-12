from dataclasses import dataclass
from typing import Optional


@dataclass
class TelemBitBufferHandle:
    offset: int  # bit offset
    size: int  # bit size


class TelemBitBuffer:
    """
    A Python reimplementation of the C++ BitBuffer, with optional existing buffer injection.
    """
    def __init__(self, bit_size: int, buffer: Optional[bytearray] = None):
        self._bit_size = bit_size
        byte_count = (bit_size + 7) >> 3
        if buffer is not None:
            if len(buffer) < byte_count:
                raise ValueError(
                    f"Provided buffer too small: need {byte_count}, got {len(buffer)}"
                )
            self._buffer = buffer
        else:
            self._buffer = bytearray(byte_count)

    def bit_size(self) -> int:
        return self._bit_size

    def write(self, handle: TelemBitBufferHandle, data: bytes) -> None:
        """
        Write bits from 'data' into the buffer at the specified handle.
        """
        if handle.offset + handle.size > self._bit_size:
            raise ValueError("Cannot write: not enough space in buffer.")

        total_bits = handle.size
        for bit_index in range(total_bits):
            absolute_bit = handle.offset + bit_index
            byte_index = (absolute_bit >> 3)
            bit_pos = absolute_bit & 7
            src_byte = bit_index >> 3
            src_bit = bit_index & 7
            bit_val = (data[src_byte] >> src_bit) & 1
            # clear then set
            self._buffer[byte_index] &= ~(1 << bit_pos)
            self._buffer[byte_index] |= bit_val << bit_pos

    def read(self, handle: TelemBitBufferHandle) -> Optional[bytes]:
        """
        Read bits as bytes from the buffer. Returns bytes object of length ceil(size/8), or None if out of range.
        """
        if handle.offset + handle.size > self._bit_size or handle.size == 0:
            return None

        total_bits = handle.size
        out_len = (total_bits + 7) >> 3
        out = bytearray(out_len)

        for bit_index in range(total_bits):
            absolute_bit = handle.offset + bit_index
            byte_index = (absolute_bit >> 3)
            bit_pos = absolute_bit & 7
            bit_val = (self._buffer[byte_index] >> bit_pos) & 1
            dst_byte = bit_index >> 3
            dst_bit = bit_index & 7
            out[dst_byte] &= ~(1 << dst_bit)
            out[dst_byte] |= bit_val << dst_bit

        return bytes(out)
