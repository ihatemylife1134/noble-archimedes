import os
import contextlib
import runpy
import sys
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from tools import build_recomp_chunks
from tools import generate_unity_chunks
from tools.generate_resource_entries import generate_resource_entries
from tools import link_noble_archimedes


class UnityChunkGenerationTests(unittest.TestCase):
    def test_resource_record_release_entry_preserves_original_leaf(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "sub_007A7080_0x7a7080.cpp").write_text(
                "void sub_007A7080_0x7a7080() {\n    switch (ctx->pc) {\n        default: break;\n    }\n"
                + "".join(f"    // 0x{a:x}: instruction\n" for a in (0x7A7098, 0x7A7328, 0x7A7358)) + "}\n")
            source = root / "sub_0079CAE8_0x79cae8.cpp"
            original = ("void sub_0079CAE8_0x79cae8() {\n    switch (ctx->pc) {\n"
                        "        case 0x79cb14u: goto label_79cb14;\n        default: break;\n    }\n"
                        "    // 0x79cae8: preceding routine\n    preceding_call();\n"
                        "label_79cb14:\n    clear_object_24();\n    return;\n"
                        "    // 0x79cb28: addiu a1, a1, 4\n    original_addiu();\n"
                        "    // 0x79cb2c: lw v0, 0(a1)\n    original_body();\n"
                        "    // 0x79cb5c: jr ra\n    original_return();\n"
                        "    // 0x79cb60: sw zero, 0x1c(a0) (Delay Slot)\n    original_delay_slot();\n}\n")
            source.write_text(original)
            output = generate_resource_entries(root)
            result = output.read_text()
            expected = original.replace("void sub_0079CAE8_0x79cae8(",
                                        "inline void noble_resource_record_release_entries(", 1)
            expected = expected.replace("        default: break;",
                                        "        case 0x79cb28u: goto label_79cb28;\n        default: break;", 1)
            expected = expected.replace("    // 0x79cb28:", "label_79cb28:\n    // 0x79cb28:", 1)
            self.assertIn(expected, result)
            self.assertEqual(source.read_text(), original)
            stamp = output.stat().st_mtime_ns
            generate_resource_entries(root)
            self.assertEqual(output.stat().st_mtime_ns, stamp)

    def test_scene_callback_entry_preserves_original_prologue(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "sub_007A7080_0x7a7080.cpp").write_text(
                "void sub_007A7080_0x7a7080() {\n    switch (ctx->pc) {\n        default: break;\n    }\n"
                + "".join(f"    // 0x{a:x}: instruction\n" for a in (0x7A7098, 0x7A7328, 0x7A7358)) + "}\n")
            source = root / "sub_00471D58_0x471d58.cpp"
            original = ("void sub_00471D58_0x471d58() {\n    switch (ctx->pc) {\n"
                        "        case 0x471de8u: goto label_471de8;\n        default: break;\n    }\n"
                        "    // 0x471d58: preceding leaf\n    preceding_leaf();\n    return;\n"
                        "    // 0x471db8: addiu sp, sp, -0x30\n    save_registers();\n"
                        "label_471de8:\n    original_body();\n}\n")
            source.write_text(original)
            result = generate_resource_entries(root).read_text()
            self.assertIn("inline void noble_scene_object_entries(", result)
            self.assertIn("case 0x471db8u: goto label_471db8;", result)
            self.assertIn("label_471db8:\n    // 0x471db8: addiu sp, sp, -0x30\n    save_registers();", result)
            self.assertEqual(source.read_text(), original)

    def test_animation_update_entry_preserves_its_prologue(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "sub_007A7080_0x7a7080.cpp").write_text(
                "void sub_007A7080_0x7a7080() {\n    switch (ctx->pc) {\n        default: break;\n    }\n"
                + "".join(f"    // 0x{a:x}: instruction\n" for a in (0x7A7098, 0x7A7328, 0x7A7358)) + "}\n")
            source = root / "sub_00794898_0x794898.cpp"
            source.write_text("void sub_00794898_0x794898() {\n    switch (ctx->pc) {\n        default: break;\n    }\n"
                              "    // 0x794ea0: addiu sp, sp, -0xe0\n    save_registers();\n}\n")
            result = generate_resource_entries(root).read_text()
            self.assertIn("case 0x794ea0u: goto label_794ea0;", result)
            self.assertIn("label_794ea0:\n    // 0x794ea0: addiu sp, sp, -0xe0\n    save_registers();", result)

    def test_resource_callback_entries_preserve_generated_code(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "sub_007A7080_0x7a7080.cpp"
            original = "void sub_007A7080_0x7a7080() {\n    switch (ctx->pc) {\n        default: break;\n    }\n"
            for address in (0x7A7098, 0x7A7328, 0x7A7358):
                original += f"    // 0x{address:x}: original instruction\n"
            source.write_text(original + "}\n")
            output = generate_resource_entries(root)
            result = output.read_text()
            for address in (0x7A7098, 0x7A7328, 0x7A7358):
                self.assertIn(f"case 0x{address:x}u: goto label_{address:x};", result)
                self.assertIn(f"label_{address:x}:\n    //", result)
            self.assertEqual(source.read_text(), original + "}\n")
            stamp = output.stat().st_mtime_ns
            generate_resource_entries(root)
            self.assertEqual(output.stat().st_mtime_ns, stamp)

    def test_cross_boundary_delay_slot_is_restored_once(self):
        source = Path("sub_004FFDC0_0x4ffdc0.cpp")
        original = "    SET_GPR_U32(ctx, 31, 0x500004u);\n"
        fixed = generate_unity_chunks._apply_split_delay_slot_fix(source, original)
        self.assertIn("ctx->f[13] = FPU_MOV_S(ctx->f[12]);", fixed)
        self.assertEqual(generate_unity_chunks._apply_split_delay_slot_fix(source, fixed), fixed)
        self.assertEqual(generate_unity_chunks._apply_split_delay_slot_fix(Path("other.cpp"), original), original)

    def test_sound_bank_compatibility_is_persisted_in_only_target_chunks(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            generated, chunks = root / "generated", root / "chunks"
            generated.mkdir()
            status = generated / "sub_0042FD28_0x42fd28.cpp"
            status.write_text("void sub_0042FD28_0x42fd28() {\n"
                              "    FAST_WRITE16(0xAD82B0u, 0x0003);\n"
                              "    SET_GPR_S32(ctx, 2, 1);\n}\n")
            queue = generated / "sub_00431128_0x431128.cpp"
            queue.write_text("void sub_00431128_0x431128() {\n"
                             "        WRITE32(ADD32(GPR_U32(ctx, 5), 8), GPR_U32(ctx, 7));\n}\n")
            generate_unity_chunks.generate_chunks(generated, chunks, num_chunks=3)
            emitted = [p.read_text() for p in sorted(chunks.glob("*.cpp"))]
            self.assertEqual(sum('sound_bank_compat.hpp' in s for s in emitted), 2)
            self.assertEqual(sum('noble_sound::bankStatus(' in s for s in emitted), 1)
            self.assertEqual(sum('noble_sound::acceptedCommand(' in s for s in emitted), 1)
            self.assertFalse(any('FAST_WRITE16(0xAD82B0u, 0x0003)' in s for s in emitted))
            self.assertIn('FAST_WRITE16', status.read_text())
            self.assertEqual(generate_unity_chunks.generate_chunks(generated, chunks, 3), [])

    def test_dispatch_transfer_fix_is_applied_once_to_both_helpers_only(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            generated = root / "generated"
            chunks = root / "chunks"
            generated.mkdir()
            helpers = {
                "sub_00420450_0x420450.cpp": (
                    "void sub_00420450_0x420450(uint8_t* rdram, R5900Context* ctx, PS2Runtime* runtime) {\n"
                    "    switch (ctx->pc) {\n"
                    "        default: break;\n"
                    "    }\n"
                    "}\n"
                ),
                "sub_0041FFF0_0x41fff0.cpp": (
                    "void sub_0041FFF0_0x41fff0(uint8_t* rdram, R5900Context* ctx, PS2Runtime* runtime) {\n"
                    "    switch (ctx->pc) {\n"
                    "        default: break;\n"
                    "    }\n"
                    "}\n"
                ),
            }
            for name, source in helpers.items():
                (generated / name).write_text(source, encoding="utf-8")

            generate_unity_chunks.generate_chunks(generated, chunks, num_chunks=1)
            chunk = chunks / "recomp_chunk_00.cpp"
            emitted = chunk.read_text(encoding="utf-8")
            guard = "if (runtime->guestDispatchDepth() != 0 && runtime->eeScheduler().currentContext() == ctx)"
            self.assertEqual(emitted.count('#include "runtime/ee_scheduler.h"'), 1)
            self.assertEqual(emitted.count(guard), 2)
            for function_name in ("sub_00420450_0x420450", "sub_0041FFF0_0x41fff0"):
                function = emitted[emitted.index(f"void {function_name}"):]
                self.assertLess(function.index(guard), function.index("switch (ctx->pc)"))
            for name, source in helpers.items():
                self.assertEqual((generated / name).read_text(encoding="utf-8"), source)

            # Match the canonical generated-source spelling, including its
            # line break and unsigned-zero suffix.
            helper = generated / "sub_00420450_0x420450.cpp"
            already_patched = helpers[helper.name].replace(
                "    switch (ctx->pc) {",
                "    if (runtime->guestDispatchDepth() != 0u &&\n"
                "        runtime->eeScheduler().currentContext() == ctx) {\n"
                "        throw EeDispatcherTransfer{};\n"
                "    }\n\n"
                "    switch (ctx->pc) {",
            )
            helper.write_text(already_patched, encoding="utf-8")
            generate_unity_chunks.generate_chunks(generated, chunks, num_chunks=1)
            emitted = chunk.read_text(encoding="utf-8")
            self.assertEqual(emitted.count('#include "runtime/ee_scheduler.h"'), 1)
            canonical_guard = (
                "if (runtime->guestDispatchDepth() != 0u && "
                "runtime->eeScheduler().currentContext() == ctx)"
            )
            normalized = " ".join(emitted.split())
            self.assertEqual(normalized.count(canonical_guard), 1)
            self.assertEqual(normalized.count(guard), 1)
            self.assertEqual(emitted.count("throw EeDispatcherTransfer{};"), 2)

            ordinary_generated = root / "ordinary_generated"
            ordinary_chunks = root / "ordinary_chunks"
            ordinary_generated.mkdir()
            ordinary = ordinary_generated / "sub_00400000_0x400000.cpp"
            ordinary.write_text("void sub_00400000() { int value = 1; }\n", encoding="utf-8")
            generate_unity_chunks.generate_chunks(ordinary_generated, ordinary_chunks, num_chunks=1)
            ordinary_emitted = (ordinary_chunks / "recomp_chunk_00.cpp").read_text(encoding="utf-8")
            self.assertIn("void sub_00400000() { int value = 1; }", ordinary_emitted)
            self.assertNotIn('#include "runtime/ee_scheduler.h"', ordinary_emitted)
            self.assertNotIn(guard, ordinary_emitted)

    def test_builder_syncs_generated_functions_before_compiling(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            generated = root / "generated"
            chunks = root / "chunks"
            generated.mkdir()
            function = generated / "sub_00400000_0x400000.cpp"
            function.write_text("void sub_00400000() { int value = 1; }\n", encoding="utf-8")
            compile_calls = []

            def fake_compile(command, capture_output, text, **kwargs):
                source = Path(command[command.index("-c") + 1])
                obj = Path(command[command.index("-o") + 1])
                depfile = Path(command[command.index("-MF") + 1])
                obj.parent.mkdir(parents=True, exist_ok=True)
                obj.write_bytes(b"object")
                depfile.write_text(f"{obj.as_posix()}: {source.as_posix()}\n", encoding="utf-8")
                compile_calls.append(command)
                return SimpleNamespace(returncode=0, stderr="")

            with patch.object(build_recomp_chunks.subprocess, "run", side_effect=fake_compile):
                build_recomp_chunks.build_chunks(generated, chunks, num_chunks=1, max_workers=1)
                function.write_text("void sub_00400000() { int value = 2; }\n", encoding="utf-8")
                os.utime(function, (time.time() + 2, time.time() + 2))
                build_recomp_chunks.build_chunks(generated, chunks, num_chunks=1, max_workers=1)

            self.assertEqual(len(compile_calls), 2)
            self.assertIn("int value = 2", (chunks / "recomp_chunk_00.cpp").read_text(encoding="utf-8"))

    def test_generation_leaves_unchanged_chunk_timestamp_alone(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            generated = root / "generated"
            chunks = root / "chunks"
            generated.mkdir()
            (generated / "sub_00400000_0x400000.cpp").write_text(
                "void sub_00400000() {}\n", encoding="utf-8"
            )

            generate_unity_chunks.generate_chunks(generated, chunks, num_chunks=1)
            chunk = chunks / "recomp_chunk_00.cpp"
            before = chunk.stat().st_mtime_ns
            time.sleep(0.02)
            generate_unity_chunks.generate_chunks(generated, chunks, num_chunks=1)

            self.assertEqual(chunk.stat().st_mtime_ns, before)


class ObjectFreshnessTests(unittest.TestCase):
    def test_header_newer_than_object_marks_object_stale(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "chunk.cpp"
            header = root / "runtime.h"
            obj = root / "chunk.o"
            depfile = root / "chunk.o.d"
            source.write_text("", encoding="utf-8")
            header.write_text("", encoding="utf-8")
            obj.write_bytes(b"object")
            now = time.time()
            os.utime(source, (now - 20, now - 20))
            os.utime(header, (now + 10, now + 10))
            os.utime(obj, (now, now))
            depfile.write_text(
                f"{obj.as_posix()}: {source.as_posix()} {header.as_posix()}\n", encoding="utf-8"
            )

            self.assertFalse(build_recomp_chunks.object_is_current(obj, source, depfile))

    def test_changed_compiler_flags_mark_object_stale(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "chunk.cpp"
            obj = root / "chunk.o"
            depfile = root / "chunk.o.d"
            source.write_text("", encoding="utf-8")
            obj.write_bytes(b"object")
            now = time.time()
            os.utime(source, (now - 20, now - 20))
            os.utime(obj, (now, now))
            depfile.write_text(f"{obj.as_posix()}: {source.as_posix()}\n", encoding="utf-8")

            # No stamp: built before flags were recorded.
            self.assertFalse(build_recomp_chunks.object_is_current(obj, source, depfile, flags=["-O2"]))
            build_recomp_chunks.flags_file(obj).write_text("-O0", encoding="utf-8")
            self.assertFalse(build_recomp_chunks.object_is_current(obj, source, depfile, flags=["-O2"]))
            build_recomp_chunks.flags_file(obj).write_text("-O2", encoding="utf-8")
            self.assertTrue(build_recomp_chunks.object_is_current(obj, source, depfile, flags=["-O2"]))
            # Callers that do not pass flags keep the dependency-only check.
            self.assertTrue(build_recomp_chunks.object_is_current(obj, source, depfile))


class LinkOutputTests(unittest.TestCase):
    def test_gpu_link_manifest_preserves_archive_paths_and_rejects_missing_inputs(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest = root / link_noble_archimedes.PGS_LINK_INPUTS
            manifest.parent.mkdir(parents=True)
            archive = root / "GPU libraries" / "libparallel-gs.a"
            archive.parent.mkdir()
            archive.write_bytes(b"archive")
            manifest.write_text(f"{archive.as_posix()}\n-lsetupapi\n", encoding="utf-8")
            self.assertEqual(link_noble_archimedes.optional_gpu_link_inputs(root),
                             [archive.as_posix(), "-lsetupapi"])
            archive.unlink()
            with self.assertRaisesRegex(FileNotFoundError, "Missing GPU link input"):
                link_noble_archimedes.optional_gpu_link_inputs(root)

    def _create_current_object(self, root, object_path, source_path=None):
        object_path = root / object_path
        source_path = root / source_path if source_path else object_path.with_suffix(".cpp")
        object_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.write_text("", encoding="utf-8")
        object_path.write_bytes(b"object")
        dependency = object_path.with_suffix(object_path.suffix + ".d")
        dependency.write_text(
            f"{object_path.as_posix()}: {source_path.as_posix()}\n", encoding="utf-8"
        )
        return object_path, dependency

    def _create_link_inputs(self, root):
        host_sources = {
            "src/main.o": "src/main.cpp",
            "src/camera/camera_controller.o": "src/camera/camera_controller.cpp",
            "src/input/input_manager.o": "src/input/input_manager.cpp",
            "src/ui/modern_overlay.o": "src/ui/modern_overlay.cpp",
            "src/vfs/iso_vfs.o": "src/vfs/iso_vfs.cpp",
            "src/recomp/register_functions.o": "src/recomp/generated/register_functions.cpp",
            "src/recomp/runtime_stub_registry.o": "src/recomp/runtime_stub_registry.cpp",
            "src/recomp/sound_bank_compat.o": "src/recomp/sound_bank_compat.cpp",
        }
        for obj, source in host_sources.items():
            self._create_current_object(root, obj, source)
        for index in range(32):
            self._create_current_object(
                root,
                f"src/recomp/chunks/recomp_chunk_{index:02d}.o",
                f"src/recomp/chunks/recomp_chunk_{index:02d}.cpp",
            )
        self._create_current_object(
            root,
            "src/recomp/chunks/recomp_chunk_entries.o",
            "src/recomp/chunks/recomp_chunk_entries.cpp",
        )

    def test_optional_output_path_keeps_default_executable_untouched(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self._create_link_inputs(root)

            candidate = root / "output" / "candidate.exe"
            candidate.parent.mkdir(parents=True)

            def fake_link(command, **kwargs):
                output = Path(command[command.index("-o") + 1])
                (root / output).write_bytes(b"linked candidate")
                return SimpleNamespace(returncode=0, stderr="")

            script = Path(__file__).parents[1] / "tools" / "link_noble_archimedes.py"
            with patch.object(sys, "argv", [str(script), str(candidate)]), patch(
                "subprocess.run", side_effect=fake_link
            ), contextlib.chdir(root):
                namespace = runpy.run_path(str(script))
                linker = namespace.get("link_executable")
                self.assertTrue(callable(linker), "linker should expose a callable for an explicit output path")
                linker(candidate, root=root)

            self.assertEqual(candidate.read_bytes(), b"linked candidate")
            self.assertFalse((root / "NobleArchimedes.exe").exists())

    def test_link_rejects_a_missing_expected_chunk_even_with_an_extra_object(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self._create_link_inputs(root)
            chunk_dir = root / "src" / "recomp" / "chunks"
            (chunk_dir / "recomp_chunk_19.o").unlink()
            (chunk_dir / "recomp_chunk_33.o").write_bytes(b"extra")

            with self.assertRaisesRegex(FileNotFoundError, "recomp_chunk_19.o"):
                link_noble_archimedes.build_link_command(root / "candidate.exe", root=root)

    def test_link_rejects_objects_without_recorded_header_dependencies(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self._create_link_inputs(root)
            dependency_file = root / "src" / "recomp" / "chunks" / "recomp_chunk_02.o.d"
            dependency_file.unlink()

            with self.assertRaisesRegex(FileNotFoundError, "recomp_chunk_02.o"):
                link_noble_archimedes.build_link_command(root / "candidate.exe", root=root)


if __name__ == "__main__":
    unittest.main()
