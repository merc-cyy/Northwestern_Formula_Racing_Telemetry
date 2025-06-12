import unittest
from dataclasses import dataclass
from typing import Optional
from analysis.common.parsers.telem.bit_buffer import TelemBitBuffer, TelemBitBufferHandle

class TestTelemBitBuffer(unittest.TestCase):
    def test_init_and_byte_size(self):
        # Test bit_size() and internal buffer length
        for bits in [0, 1, 7, 8, 9, 16, 24, 32]:
            buf = TelemBitBuffer(bit_size=bits)
            self.assertEqual(buf.bit_size(), bits)
            # internal buffer length should be ceil(bits/8) + 1 (offset hack)
            expected_bytes = ((bits + 7) // 8) + 1
            self.assertEqual(len(buf._buffer), expected_bytes)

    def test_byte_aligned_write_read(self):
        buf = TelemBitBuffer(bit_size=8)
        value = 0xAB
        handle = TelemBitBufferHandle(offset=0, size=8)
        # write expects bytes of length 1
        buf.write(handle, bytes([value]))
        data = buf.read(handle)
        self.assertEqual(data, bytes([value]))

    def test_within_byte_write_read(self):
        buf = TelemBitBuffer(bit_size=8)
        value = 0x5  # 4-bit value
        handle = TelemBitBufferHandle(offset=0, size=4)
        buf.write(handle, bytes([value]))
        data = buf.read(handle)
        # lower 4 bits
        self.assertIsNotNone(data)
        self.assertEqual(data[0] & 0xF, value)

    def test_cross_byte_write_read(self):
        buf = TelemBitBuffer(bit_size=16)
        # 12-bit value 0xABC (only lower 12 bits)
        value = 0xABC
        # Represent in 2 bytes
        raw = value.to_bytes(2, byteorder='little')
        handle = TelemBitBufferHandle(offset=4, size=12)
        buf.write(handle, raw)
        data = buf.read(handle)
        self.assertIsNotNone(data)
        # reconstruct integer
        result = int.from_bytes(data, byteorder='little') & 0xFFF
        self.assertEqual(result, value & 0xFFF)

    def test_out_of_range_write_error(self):
        buf = TelemBitBuffer(bit_size=8)
        handle = TelemBitBufferHandle(offset=4, size=8)  # 4+8=12>8
        with self.assertRaises(ValueError):
            buf.write(handle, bytes([0xFF]))
        # read returns None
        data = buf.read(handle)
        self.assertIsNone(data)

    def test_zero_size_handle_read(self):
        buf = TelemBitBuffer(bit_size=8)
        handle = TelemBitBufferHandle(offset=0, size=0)
        data = buf.read(handle)
        self.assertIsNone(data)

    def test_provided_buffer_too_small(self):
        # required bytes = ceil(16/8)+1 = 3
        small = bytearray(2)
        with self.assertRaises(ValueError):
            TelemBitBuffer(bit_size=16, buffer=small)
        # correct size works
        ok_buf = bytearray(3)
        bb = TelemBitBuffer(bit_size=16, buffer=ok_buf)
        self.assertEqual(bb._buffer, ok_buf)

    def test_random_nonoverlapping_writes(self):
        import random
        random.seed(0)
        buf = TelemBitBuffer(bit_size=64)
        for _ in range(10):
            offset = random.randint(0, 60)
            size = random.choice([4, 8, 12])
            if offset + size > 64:
                continue
            max_val = (1 << size) - 1
            val = random.randint(0, max_val)
            raw = val.to_bytes((size + 7) // 8, byteorder='little')
            handle = TelemBitBufferHandle(offset=offset, size=size)
            buf.write(handle, raw)
            data = buf.read(handle)
            self.assertIsNotNone(data)
            result = int.from_bytes(data, byteorder='little') & max_val
            self.assertEqual(result, val)

if __name__ == '__main__':
    unittest.main()
