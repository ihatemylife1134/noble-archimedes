"""Synthetic instruction tests for locally generated guest entry adapters."""
import importlib
import importlib.util
from pathlib import Path
import tempfile
import unittest


def immediate(opcode, source, target, value):
    return (opcode << 26) | (source << 21) | (target << 16) | (value & 0xffff)


def special(source, target, destination, function):
    return (source << 21) | (target << 16) | (destination << 11) | function


def source_text(start, words):
    return "".join(f"    // 0x{start + 4 * i:x}: 0x{word:x} synthetic\n"
                   for i, word in enumerate(words))


class GuestEntryGenerationTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(importlib.util.find_spec("tools.generate_guest_entries"),
                             "local guest-entry generator must exist")
        self.generator = importlib.import_module("tools.generate_guest_entries")

    def entry(self, name="example", start=0x1200, words=None):
        if words is None:
            words = [immediate(15, 0, 9, 0x1234), immediate(9, 0, 8, -3),
                     immediate(43, 9, 6, -12), special(25, 0, 0, 8),
                     special(0, 7, 8, 11)]
        return self.generator.Entry("local.cpp", name, start, start + 4 * (len(words) - 1)), words

    def generate(self, root, spec, words):
        (root / spec.source).write_text(source_text(spec.start, words), encoding="utf-8")
        return self.generator.generate_guest_entries(root, root / "adapter.hpp", (spec,))

    def test_values_come_from_local_instruction_words(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            spec, words = self.entry()
            text = self.generate(root, spec, words).read_text()
            self.assertIn("SET_GPR_S32(ctx, 9, 0x12340000);", text)
            self.assertIn("SET_GPR_S32(ctx, 8, -3);", text)
            self.assertIn("WRITE32(0x1233FFF4u, GPR_U32(ctx, 6));", text)
            self.assertIn("const uint32_t target = GPR_U32(ctx, 25);", text)
            self.assertIn("if (GPR_U64(ctx, 7) != 0) SET_GPR_VEC(ctx, 8, GPR_VEC(ctx, 0));", text)
            self.assertIn("registerFunction(0x1200u, example);", text)
            self.assertNotIn("ctx->branch_pc", text)
            self.assertNotIn("ctx->in_delay_slot", text)

    def test_load_base_cache_and_jump_delay_order(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target = 0x345670
            words = [special(12, 0, 4, 45), immediate(55, 29, 16, 0),
                     special(0, 0, 5, 45), immediate(55, 29, 17, 24),
                     (2 << 26) | (target >> 2), immediate(9, 29, 29, 40)]
            spec, words = self.entry(start=0x1800, words=words)
            text = self.generate(root, spec, words).read_text()
            self.assertIn("SET_GPR_U64(ctx, 4, GPR_U64(ctx, 12));", text)
            self.assertIn("const uint32_t sp = GPR_U32(ctx, 29);", text)
            self.assertIn("SET_GPR_U64(ctx, 16, READ64(sp));", text)
            self.assertIn("SET_GPR_U64(ctx, 17, READ64(sp + 24));", text)
            self.assertIn("SET_GPR_U64(ctx, 5, 0);", text)
            delay = "SET_GPR_S32(ctx, 29, static_cast<int32_t>(sp + 40));"
            self.assertLess(text.index(delay), text.index("ctx->pc = 0x345670u;"))
            self.assertIn("ctx, 0x345670u, 0x1810u, 0u,", text)

    def test_changed_load_base_is_not_cached(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            words = [immediate(55, 10, 11, -8), immediate(9, 10, 10, 4),
                     immediate(55, 10, 12, 0), special(31, 0, 0, 8),
                     special(4, 5, 6, 45)]
            spec, words = self.entry(words=words)
            text = self.generate(root, spec, words).read_text()
            self.assertNotIn("const uint32_t base10", text)
            self.assertIn("READ64(ADD32(GPR_U32(ctx, 10), 4294967288))", text)
            self.assertIn("GPR_U64(ctx, 4) + GPR_U64(ctx, 5)", text)

    def test_jump_uses_pc_high_bits(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            spec, words = self.entry(start=0xA0001200,
                                     words=[(2 << 26) | (0x2340 >> 2), immediate(9, 0, 3, 1)])
            text = self.generate(root, spec, words).read_text()
            self.assertIn("ctx->pc = 0xa0002340u;", text)

    def test_unchanged_output_and_inputs_keep_timestamps_and_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            spec, words = self.entry()
            output = self.generate(root, spec, words)
            original = (root / spec.source).read_bytes()
            stamp = output.stat().st_mtime_ns
            self.generator.generate_guest_entries(root, output, (spec,))
            self.assertEqual(output.stat().st_mtime_ns, stamp)
            self.assertEqual((root / spec.source).read_bytes(), original)

    def test_missing_inputs_for_synthetic_unity_fixtures_do_nothing(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            output = root / "adapter.hpp"
            self.assertIsNone(self.generator.generate_guest_entries(root, output))
            self.assertFalse(output.exists())

    def test_unity_generation_emits_the_header_from_fresh_synthetic_sources(self):
        from tools.generate_unity_chunks import generate_chunks
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            generated = root / "generated"
            generated.mkdir()
            for entry in self.generator.ENTRIES:
                length = (entry.end - entry.start) // 4 + 1
                words = [immediate(9, 0, 21, i + 13) for i in range(length - 2)]
                words += [(2 << 26) | (0xabc0 >> 2), immediate(9, 7, 7, 5)]
                (generated / entry.source).write_text(source_text(entry.start, words))
            generate_chunks(generated, root / "chunks", num_chunks=2)
            output = root / "guest_entry_compat.hpp"
            self.assertTrue(output.exists())
            self.assertIn("SET_GPR_S32(ctx, 21, 13);", output.read_text())
            self.assertIn("ctx->pc = 0xabc0u;", output.read_text())

    def test_partially_missing_sources_reject(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            first, words = self.entry()
            second = self.generator.Entry("missing.cpp", "second", 0x2000, 0x2004)
            (root / first.source).write_text(source_text(first.start, words))
            with self.assertRaisesRegex(ValueError, "Missing.*missing.cpp"):
                self.generator.generate_guest_entries(root, root / "adapter.hpp", (first, second))

    def test_malformed_sources_reject_without_replacing_an_existing_output(self):
        spec, words = self.entry()
        valid = source_text(spec.start, words)
        malformed = {
            "missing": valid.replace(valid.splitlines(keepends=True)[1], ""),
            "duplicate": valid + valid.splitlines(keepends=True)[0],
            "wide word": valid.replace(f"0x{words[0]:x}", "0x100000000"),
            "unsupported": source_text(spec.start, [immediate(8, 0, 9, 1), *words[1:]]),
            "branch position": source_text(spec.start, [words[3], *words[1:]]),
            "no branch": source_text(spec.start, [*words[:3], words[4], words[4]]),
            "control in delay": source_text(spec.start, [*words[:4], words[3]]),
            "reserved JR": source_text(spec.start, [*words[:3], words[3] | (1 << 16), words[4]]),
            "reserved LUI": source_text(spec.start, [words[0] | (1 << 21), *words[1:]]),
            "shifted DADDU": source_text(spec.start, [*words[:4], special(4, 5, 6, 45) | (1 << 6)]),
        }
        for label, text in malformed.items():
            with self.subTest(label=label), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                (root / spec.source).write_text(text)
                output = root / "adapter.hpp"
                output.write_bytes(b"preserve me\r\n")
                with self.assertRaises(ValueError):
                    self.generator.generate_guest_entries(root, output, (spec,))
                self.assertEqual(output.read_bytes(), b"preserve me\r\n")

    def test_local_ignored_header_matches_translation_without_writing_it(self):
        repo = Path(__file__).resolve().parents[1]
        generated = repo / "src/recomp/generated"
        output = repo / "src/recomp/guest_entry_compat.hpp"
        if not output.exists() or not all((generated / entry.source).exists()
                                         for entry in self.generator.ENTRIES):
            self.skipTest("local game-derived inputs are intentionally absent from a fresh checkout")
        self.assertEqual(self.generator.render_guest_entries(generated).encode("utf-8"),
                         output.read_bytes())


if __name__ == "__main__":
    unittest.main()
