"""Prepare a fresh, explicitly selected source export; never copy Git history."""
from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "tools/PS2Recomp"
PIN = "75d729ce40d7eed9649fd4bb05628dee520f3d0c"
DOCS = ["README.md", "BUILDING.md", "CONTRIBUTING.md", "THIRD_PARTY_NOTICES.md", "docs/BUILD_VARIANTS.md",
        "docs/PROJECT_STATUS.md", "docs/PUBLICATION.md", "docs/DEVELOPMENT_BUILD_NOTES.md"]
ROOT_FILES = [".gitattributes", ".gitmodules", "CMakeLists.txt",
              "cvcod_ps2recomp_config.toml", "cvcod_recomp_config.toml"]
SOURCE_DIRS = ["src/camera", "src/input", "src/ui", "src/vfs", "src/render", "src/platform"]
GLUE = ["src/main.cpp", "src/recomp/runtime_stub_registry.cpp",
        "src/recomp/runtime_stub_registry.hpp", "src/recomp/sound_bank_callbacks.hpp",
        "src/recomp/sound_bank_compat.cpp", "src/recomp/sound_bank_compat.hpp"]
TOOLS = ["build_recomp_chunks.py", "link_noble_archimedes.py", "ps2_iso_reader.py",
         "cvcod_elf_analyzer.py", "generate_guest_entries.py", "generate_resource_entries.py",
         "generate_stub_registry.py", "generate_unity_chunks.py", "generate_entry_chunk.py",
         "optimize_register_functions.py", "prepare_publication.py"]
TESTS = ["tests/test_build_helpers.py", "tests/test_guest_entries_generation.py",
         "tests/renderer_settings_test.cpp", "tools/tests/test_optimize_register_functions.py"]
GS = ["README.md", "CMakeLists.txt", "bootstrap.py", "build.py", "consumer.cpp",
      "host_glue.cpp", "pcsx2_gs_abi.h", "pcsx2_gs_fp_scope.hpp", "toolchain_check.cpp", "test_real_module.py"]
EXTRA_RUNTIME = [
    "ps2xRuntime/cmake/ParallelGs.cmake",
    "ps2xRuntime/include/runtime/ee_dispatch_policy.h",
    "ps2xRuntime/include/runtime/host_profile.h",
    "ps2xRuntime/include/runtime/ps2_async_stdio.h",
    "ps2xRuntime/include/runtime/ps2_guest_dispatch_state.h",
    "ps2xRuntime/include/runtime/vif1_worker_device.h",
    "ps2xRuntime/scripts/fetch_parallel_gs.py",
    "ps2xRuntime/src/lib/Kernel/Stubs/Helpers/GuestWriteSpan.h",
    "ps2xRuntime/src/lib/gs/gs_menu_row.h",
    "ps2xRuntime/src/lib/gs/gs_pgs_logical_scanout.h",
    "ps2xRuntime/src/lib/gs/gs_pgs_profile.h",
    "ps2xRuntime/src/lib/gs/gs_raw_backend_feed.h",
    "ps2xRuntime/src/lib/gs/gs_raw_feed.h",
    "ps2xRuntime/src/lib/gs/gs_upload_policy.h",
    "ps2xRuntime/src/lib/gs/ps2_gs_pcsx2_bridge.cpp",
    "ps2xRuntime/src/lib/gs/ps2_gs_pcsx2_bridge.h",
    "ps2xRuntime/src/lib/gs/ps2_gs_pgs_bridge.cpp",
    "ps2xRuntime/src/lib/gs/ps2_gs_pgs_bridge.h",
    "ps2xRuntime/src/lib/guest_dispatch_snapshot.h",
    "ps2xRuntime/src/lib/ps2_async_stdio.cpp",
    "ps2xRuntime/src/lib/ps2_host_sampler.cpp",
    "ps2xRuntime/src/lib/dmac_pending_count.h",
    "ps2xRuntime/src/lib/vif1_worker_memory.cpp",
    "ps2xRuntime/src/lib/vif1_worker_memory_internal.inc",
    "ps2xRuntime/src/lib/vif1_worker_queue.h",
    "ps2xRuntime/src/lib/vu/ps2_vu1_capture.h",
    "ps2xRuntime/src/lib/vu/ps2_vu1_native.h",
    "ps2xRuntime/src/lib/vu/vu_fmac_math.h",
    "ps2xRuntime/third_party/parallel-gs-transfer-fragments.patch",
]
ALLOWED_SUFFIX = {".md", ".py", ".cpp", ".hpp", ".h", ".toml", ".txt", ".patch", ".json"}
SECRET = re.compile(r"(?:gh[pousr]_[A-Za-z0-9]{25,}|github_pat_[A-Za-z0-9_]{30,}|-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----)")

def git(*args, cwd=ROOT):
    return subprocess.check_output(["git", *args], cwd=cwd)

def validate_text(name, data):
    assert b"\0" not in data, f"Binary rejected: {name}"
    text = data.decode("utf-8-sig")
    assert not SECRET.search(text), f"Credential pattern rejected: {name}"
    assert not text.startswith(("MZ", "\x7fELF")), f"Executable rejected: {name}"
    return text

def main(destination):
    dest = Path(destination).resolve()
    assert dest != ROOT and ROOT not in dest.parents, "Export must be outside development tree"
    assert not dest.exists(), "Use a fresh destination; existing directories are preserved"
    assert git("rev-parse", "HEAD", cwd=RUNTIME).decode().strip() == PIN
    selected = DOCS + ROOT_FILES + GLUE + TESTS
    selected += ["tools/" + p for p in TOOLS]
    selected += ["tools/pcsx2_gs/" + p for p in GS]
    for directory in SOURCE_DIRS:
        selected += [p.relative_to(ROOT).as_posix() for p in (ROOT/directory).iterdir()
                     if p.is_file() and p.suffix in {".h", ".hpp", ".cpp"}]
    payloads = {}
    for name in sorted(set(selected)):
        assert Path(name).suffix in ALLOWED_SUFFIX or name in {".gitattributes", ".gitmodules"}
        data = (ROOT/name).read_bytes()
        validate_text(name, data)
        payloads[name] = data
    patch = git("diff", "--no-ext-diff", "--full-index", PIN, "--", ".", ":(exclude).gitignore", cwd=RUNTIME)
    for name in EXTRA_RUNTIME:
        assert not git("ls-files", "--", name, cwd=RUNTIME).strip(), name
        source = (RUNTIME/name).read_bytes().decode("utf-8-sig").replace("\r\n", "\n")
        assert source.endswith("\n"), name
        patch += (f"diff --git a/{name} b/{name}\nnew file mode 100644\n"
                  f"--- /dev/null\n+++ b/{name}\n@@ -0,0 +1,{len(source.splitlines())} @@\n" +
                  "".join("+" + line + "\n" for line in source.splitlines())).encode()
    patch_text = validate_text("runtime patch", patch)
    assert "GIT binary patch" not in patch_text
    patch_paths = re.findall(r"^diff --git a/(.*?) b/.*$", patch_text, re.M)
    assert all(not p.startswith(("build/", "output/", "graphify-out/")) for p in patch_paths)
    assert all(Path(p).suffix in {".cpp", ".h", ".hpp", ".inc", ".txt", ".cmake", ".py", ".patch"} for p in patch_paths)
    payloads["patches/ps2recomp-progress.patch"] = patch
    payloads["licenses/PS2Recomp-GPL-3.0.md"] = (RUNTIME/"LICENSE").read_bytes()
    payloads[".gitignore"] = (ROOT/".gitignore").read_bytes() + b"\n# Public source: never admit local game/research payloads\noutput/\nextracted/\nmc0/\nmc1/\n*.elf\n*.irx\n*.rom\n*.bios\n*.spv\n*.sav\n*.ps2\n*.o.flags\n*.o.d\nresource_entry_aliases.hpp\nPUBLICATION_CHECKS.local.json\n"
    for name, data in payloads.items():
        data = data.replace(b"\r\n", b"\n")
        if not name.endswith(".patch") and not name.startswith("licenses/"):
            data = b"\n".join(line.rstrip(b" \t") for line in data.split(b"\n"))
        payloads[name] = data
    dest.mkdir(parents=True)
    for name, data in payloads.items():
        validate_text(name, data)
        target=dest/name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    manifest = {"format": 1, "date": "2026-10-15", "runtime_base": PIN,
                "history": "fresh export; no development Git objects copied",
                "runtime_patch_paths": patch_paths,
                "files": {name: hashlib.sha256(data).hexdigest() for name,data in sorted(payloads.items())}}
    (dest/"PUBLICATION_MANIFEST.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"destination":str(dest),"files":len(payloads)+1,
                      "bytes":sum(map(len,payloads.values())),"runtime_patch_paths":len(patch_paths)}))

if __name__ == "__main__":
    main(sys.argv[1])
