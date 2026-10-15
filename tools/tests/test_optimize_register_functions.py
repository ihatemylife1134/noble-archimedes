import ctypes
import re
import tempfile
import unittest
from pathlib import Path

from tools.optimize_register_functions import optimize_register_functions


class FunctionTableRangeTests(unittest.TestCase):
    def test_generated_table_ranges_stay_within_capacity(self):
        table_path = Path(__file__).resolve().parents[2] / "src/recomp/generated/register_functions.cpp"
        if not table_path.is_file():
            self.skipTest("local game-derived inputs are intentionally absent from a fresh checkout")
        generated = table_path.read_text(encoding="utf-8")
        capacity = int(re.search(r"FunctionTableSlotCount = (\d+)u", generated).group(1))
        ends = [int(end) for end in re.findall(r"\{\s*\d+u,\s*(\d+)u,", generated)]
        self.assertTrue(ends)
        self.assertLess(max(ends), capacity)

    def test_declaration_slot_does_not_overwrite_canary(self):
        source = [
            "PS2Runtime::RecompiledFunction g_ps2RecompiledFunctionTable[4u] = {};",
            "g_ps2RecompiledFunctionTable[0u] = first;",
            "g_ps2RecompiledFunctionTable[1u] = first;",
            "g_ps2RecompiledFunctionTable[3u] = last;",
        ]
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "input.cpp"
            output_path = Path(directory) / "output.cpp"
            input_path.write_text("\n".join(source), encoding="utf-8")
            optimize_register_functions(str(input_path), str(output_path))
            generated = output_path.read_text(encoding="utf-8")
        ranges = [
            (int(start), int(end), function.strip())
            for start, end, function in re.findall(
                r"\{\s*(\d+)u,\s*(\d+)u,\s*(\{\}|[^{}]+)\s*\}", generated
            )
        ]
        table_with_canary = (ctypes.c_int * 5)(0, 0, 0, 0, 0x5A5A5A5A)
        for start, end, _ in ranges:
            for slot in range(start, end + 1):
                table_with_canary[slot] = 1

        self.assertEqual(table_with_canary[4], 0x5A5A5A5A)
        self.assertEqual(ranges, [(0, 1, "first"), (3, 3, "last")])


if __name__ == "__main__":
    unittest.main()
