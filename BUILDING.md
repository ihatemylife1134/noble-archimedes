# Build and play — developer workflow

Choose a configuration in [build variants](docs/BUILD_VARIANTS.md). The common setup and generation steps below apply to each public configuration. To work on a fork and submit changes, see [CONTRIBUTING.md](CONTRIBUTING.md).

## Scope

Established target: Windows x64, MinGW-w64 GCC/G++ 15.2, Python 3.12, CMake 3.24+, Ninja and a Vulkan driver. Incremental builds were used during development. **Clean public generation/build/play has not been qualified end-to-end.** Private optimized VU DLLs and game-specific GPU translations are excluded; these instructions do not reproduce the private benchmark binary.

Only USA PS2 **SLUS-21168** is targeted. Supply your own lawfully obtained game. Keep every game input, generated body, capture and binary local and ignored.

## Fetch and restore the runtime

```powershell
git clone --recurse-submodules https://github.com/sergiomanzur/noble-archimedes.git
cd noble-archimedes
git -C tools/PS2Recomp apply --check ../../patches/ps2recomp-progress.patch
git -C tools/PS2Recomp apply ../../patches/ps2recomp-progress.patch
```

Apply once to the pinned clean submodule. Inspect a failed check; do not force it over another runtime version.

## Local game input

Place the disc image at the root as `Castlevania - Curse of Darkness (USA).iso`. Extract the boot executable locally:

```powershell
@'
from pathlib import Path
from tools.ps2_iso_reader import PS2IsoReader
iso = PS2IsoReader("Castlevania - Curse of Darkness (USA).iso")
try:
    target = Path("extracted/SLUS_211.68")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(iso.read_file("SLUS_211.68"))
finally:
    iso.close()
'@ | python -
```

Keep the ISO for streamed assets. An ELF alone is insufficient. The executable changes its working directory to its own directory, so the asset/dependency layout must be beside it.

## Configure dependencies and compiler

Run where `g++`, `cmake`, `ninja`, `python` and `git` are available. This is the expected setup rather than a newly certified clean-build recipe:

```powershell
python tools/PS2Recomp/ps2xRuntime/scripts/fetch_parallel_gs.py
cmake -S tools/PS2Recomp -B tools/PS2Recomp/build -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_COMPILER=gcc -DCMAKE_CXX_COMPILER=g++ -DPS2X_BUILD_STUDIO=OFF -DPS2X_BUILD_TEST=OFF -DPS2X_ENABLE_PGS=ON
cmake --build tools/PS2Recomp/build --target ps2_recomp ps2_runtime ps2_iop --parallel 2
```

CMake fetches window/UI libraries and Windows FFmpeg; network and upstream toolchain requirements apply. The manual linker expects these paths relative to `tools/PS2Recomp/build`:

- `ps2xRuntime/libps2_runtime.a`, `librlImGui.a`, `libimgui.a`;
- `ps2xIOP/libps2_iop.a`;
- `_deps/raylib-build/raylib/libraylib.a`;
- `ThirdParty/ffmpeg-prefix/src/ffmpeg_external/bin/{avcodec,avformat,avutil,swresample,swscale}.lib`;
- optional GPU archive list `ps2xRuntime/pgs_link_inputs.txt`.

A portable dependency/install manifest remains missing. The root CMake target is not the established generated-chunk entry point.

## Generate guest C++ locally

Locate the built compiler and invoke it from the root:

```powershell
$recompiler = Get-ChildItem tools/PS2Recomp/build -Filter ps2_recomp.exe -Recurse | Select-Object -First 1
if (-not $recompiler) { throw "Compiler not built" }
& $recompiler.FullName cvcod_ps2recomp_config.toml
if ($LASTEXITCODE -ne 0) { throw "Guest generation failed" }
python tools/generate_stub_registry.py
python tools/optimize_register_functions.py
python tools/generate_entry_chunk.py
```

The TOML supplies discovery/binding metadata; the ELF supplies instructions. Generated bodies, entry adapters, registration and chunks stay local. Stripped-game discovery and locally maintained guest compatibility changes still need reproducibility work. Completing generation does not prove complete gameplay.

## Build and launch

```powershell
python tools/build_recomp_chunks.py --jobs 2
python tools/link_noble_archimedes.py
$env:PS2_GS_BACKEND = "pgs"
Remove-Item Env:PS2_VU_BACKEND -ErrorAction SilentlyContinue
.\NobleArchimedes.exe
```

The scripts compile 32 chunks plus the entries chunk and host objects. Full chunk builds previously took about 20 minutes on the development host. Linking rejects missing/stale objects and dependency files.

Acquire required FFmpeg/window/compiler-runtime DLLs from your dependency build or authorized packages; keep them beside the executable as required by its imports. No DLL bundle is included. Keep the ISO and `extracted/SLUS_211.68` beside the executable. An alternate ELF path can be passed as argument one.

Use arrows/game buttons to select New Game, enter a name and follow prompts. See README for controls. Sound, movies, saves and whole-game behavior remain unfinished. `PS2_GS_BACKEND=cpu` selects diagnostic CPU rendering. Overlay renderer settings apply on restart; the environment override wins.

## Optional PCSX2 GS-only hybrid

Requirements: MSVC **14.40.33807**, Windows SDK **10.0.22621.0**, CMake/Ninja and 7-Zip. `tools/pcsx2_gs/build.py` uses standard BuildTools/SDK paths from the development machine; adapt its constants for different installations.

```powershell
git clone --no-checkout https://github.com/PCSX2/pcsx2.git output/reference_sources/pcsx2
git -C output/reference_sources/pcsx2 checkout --detach 646df006a4688063e56c0826e7ea4b8bb0c112c4
git -C output/reference_sources/pcsx2 submodule update --init --recursive
python tools/pcsx2_gs/build.py toolchain
python tools/pcsx2_gs/bootstrap.py
python tools/pcsx2_gs/build.py consumer
cmake -S tools/PS2Recomp -B tools/PS2Recomp/build -DPS2X_ENABLE_PCSX2_GS=ON
cmake --build tools/PS2Recomp/build --target ps2_runtime --parallel 2
```

Bootstrap verifies the official release asset's SHA256 but resolves the asset at run time instead of pinning an immutable dependency digest in this snapshot. Toolchain/dependency reproducibility remains incomplete.

The manual host builder does not inherit CMake's `NOBLE_HAVE_PCSX2_GS=1`. Compile host objects with that definition, then link:

```powershell
@'
from tools import build_recomp_chunks as build
build.HOST_OPT_FLAGS.append("-DNOBLE_HAVE_PCSX2_GS=1")
results = build.build_host_objects()
for name, ok, seconds, message in results:
    print(name, ok, message)
if not all(row[1] for row in results):
    raise SystemExit(1)
'@ | python -
python tools/link_noble_archimedes.py
$env:PS2_PCSX2_GS_ADAPTER = (Resolve-Path output/fps60/pcsx2_gs_consumer_v1/bin/noble_pcsx2_gs.dll).Path
$env:PS2_PCSX2_GS_RESOURCES = (Resolve-Path output/reference_sources/pcsx2/bin/resources).Path
$env:PS2_GS_BACKEND = "pcsx2"
.\NobleArchimedes.exe
```

Keep package-provided transitive DLLs beside the module. Missing module/resources/ABI support is an initialization error. The adapter does not start a PCSX2 VM: this project's EE/VU/gameplay remain active. No 60 FPS gameplay claim is made. See [adapter details](tools/pcsx2_gs/README.md).

## Validation and diagnostics

```powershell
python -m unittest discover -s tests -p test_build_helpers.py
python -m unittest discover -s tests -p test_guest_entries_generation.py
```

These qualify helpers, not gameplay. Benchmark with screenshots, GS history and detailed tracing disabled. Measure actual guest updates and fresh images with ordinary movement, known module identities and normal shutdown; window FPS or VBlank alone is insufficient. See [status](docs/PROJECT_STATUS.md) and [historical notes](docs/DEVELOPMENT_BUILD_NOTES.md).
