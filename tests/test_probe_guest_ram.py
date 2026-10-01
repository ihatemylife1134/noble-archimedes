import struct
import unittest

from tools import probe_guest_ram as probe


class GuestBaseHintTests(unittest.TestCase):
    def setUp(self):
        self.base = 0x200000000
        self.memory = {
            self.base + probe.ANCHOR_ADDRESS: struct.pack("<4I", *probe.ANCHOR_WORDS),
            self.base + probe.PHASE_INDEX_ADDRESS: struct.pack("<I", 2),
            self.base + probe.PHASE_TABLE_ADDRESS + 8: struct.pack("<I", 7),
            self.base + probe.PHASE_FRAME_TABLE_ADDRESS + 8: struct.pack("<I", 123),
        }

    def read(self, address, size):
        data = self.memory.get(address)
        return data if data is not None and len(data) == size else None

    def test_hint_requires_current_game_anchor_and_complete_phase_data(self):
        self.assertEqual(probe.validate_guest_base(self.read, self.base), (self.base, 2, 7, 123))
        self.assertIsNone(probe.validate_guest_base(self.read, self.base + 0x1000))
        self.memory[self.base + probe.ANCHOR_ADDRESS] = bytes(16)
        self.assertIsNone(probe.validate_guest_base(self.read, self.base))

    def test_invalid_phase_or_unreadable_table_rejects_hint(self):
        del self.memory[self.base + probe.PHASE_FRAME_TABLE_ADDRESS + 8]
        self.assertIsNone(probe.validate_guest_base(self.read, self.base))
        self.memory[self.base + probe.PHASE_INDEX_ADDRESS] = struct.pack("<I", 16)
        self.assertIsNone(probe.validate_guest_base(self.read, self.base))
        self.assertIsNone(probe.validate_guest_base(self.read, -1))
        self.assertIsNone(probe.validate_guest_base(self.read, 0x7FFFFFFFFFFF))

    def test_explicit_hint_reports_invalid_phase_without_indexed_reads(self):
        self.memory[self.base + probe.PHASE_INDEX_ADDRESS] = struct.pack("<I", 0xFFFFFFFF)
        self.memory[self.base + probe.PHASE_TABLE_ADDRESS] = bytes(128)
        reads = []
        def read(address, size):
            reads.append((address, size))
            return self.read(address, size)
        self.assertEqual(probe.validate_guest_base(read, self.base, allow_invalid_phase=True),
                         (self.base, 0xFFFFFFFF, None, None))
        self.assertTrue(all(address < self.base + probe.PHASE_FRAME_TABLE_ADDRESS + 64
                            for address, _ in reads))
        del self.memory[self.base + probe.PHASE_TABLE_ADDRESS]
        self.assertIsNone(probe.validate_guest_base(read, self.base, allow_invalid_phase=True))


if __name__ == "__main__":
    unittest.main()
