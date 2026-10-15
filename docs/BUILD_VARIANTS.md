# Build variants for contributors

All commands are PowerShell, run from the checkout root. Read [the common build guide](../BUILDING.md) first: fetch the pinned runtime, apply its patch once, provide your own USA game input, generate guest code locally, and acquire the required runtime DLLs. These are development recipes checked against source/build-helper options, not fresh end-to-end gameplay certifications.

## Choose a path

| Configuration | Runtime CMake options | Launch selector | Availability |
| --- | --- | --- | --- |
| Native UI mode / Vulkan GS | `PS2X_ENABLE_PGS=ON`, `PS2X_ENABLE_PCSX2_GS=OFF` | `PS2_GS_BACKEND=pgs` | Public source; recommended baseline |
| CPU GS diagnostics | Both options `OFF` | `PS2_GS_BACKEND=cpu` | Public source; correctness/debugging, not the FPS target |
| Hybrid / actual PCSX2 GS | Both options `ON`; separately build MSVC GS DLL | `PS2_GS_BACKEND=pcsx2` | Public bridge/adapter source; experimental |
| Optimized native VU development module | Optional VU DLL with exact runtime ABI | `PS2_VU_BACKEND=play` only with a compatible module | Private game-derived translations excluded; no complete public regeneration/build recipe yet |
| Full native engine-seam GPU replacement | No completed public target | No production selector | Research only; not a buildable fourth renderer |

The first three configurations share recompiled EE gameplay. The public VU default is generic compatibility execution. Vulkan GS and PCSX2 GS both implement PS2 GS semantics; neither setting alone enables the unfinished engine-seam replacement.

Use a **separate clone per configuration**, each with its own `tools/PS2Recomp/build`. The manual scripts currently hard-code that build path. Passing a different CMake `-B` path alone does not retarget the scripts. Reusing a build tree can leave stale GPU link manifests, objects or host definitions; separate clones make comparisons easier to trust. Keep required game inputs local in each clone, or use your own local asset-management arrangement.

## A. Native baseline with Vulkan paraLLEl-GS

After restoring the patched runtime in a fresh checkout:

```powershell
python tools/PS2Recomp/ps2xRuntime/scripts/fetch_parallel_gs.py
cmake -S tools/PS2Recomp -B tools/PS2Recomp/build -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_COMPILER=gcc -DCMAKE_CXX_COMPILER=g++ -DPS2X_BUILD_STUDIO=OFF -DPS2X_BUILD_TEST=OFF -DPS2X_ENABLE_PGS=ON -DPS2X_ENABLE_PCSX2_GS=OFF
cmake --build tools/PS2Recomp/build --target ps2_recomp ps2_runtime ps2_iop --parallel 2
```

Now perform **Generate guest C++ locally** in [BUILDING.md](../BUILDING.md), then:

```powershell
python tools/build_recomp_chunks.py --jobs 2
python tools/link_noble_archimedes.py
Remove-Item Env:PS2_VU_BACKEND -ErrorAction SilentlyContinue
$env:PS2_GS_BACKEND = "pgs"
$env:PS2_NATIVE_VIF1_WORKER = "1"
.\NobleArchimedes.exe
```

The expected output is `NobleArchimedes.exe` at the root plus the built runtime archives. `PS2_NATIVE_VIF1_WORKER=1` opts into the asynchronous VIF1/VU worker used by the latest recovery candidate; remove the variable to compare synchronous execution. Keep the ISO, extracted ELF and dependency DLLs in the layout described in the common guide. Check startup output to confirm the renderer actually initialized; a selection variable is not proof of an active GPU backend. Generic VU execution does not reproduce the excluded optimized DLL's benchmark.

## B. CPU GS diagnostic configuration

Use a fresh separate checkout so there is no old `pgs_link_inputs.txt` from a Vulkan build. This profile needs no paraLLEl-GS fetch:

```powershell
cmake -S tools/PS2Recomp -B tools/PS2Recomp/build -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_COMPILER=gcc -DCMAKE_CXX_COMPILER=g++ -DPS2X_BUILD_STUDIO=OFF -DPS2X_BUILD_TEST=OFF -DPS2X_ENABLE_PGS=OFF -DPS2X_ENABLE_PCSX2_GS=OFF
cmake --build tools/PS2Recomp/build --target ps2_recomp ps2_runtime ps2_iop --parallel 2
```

Generate guest C++ using the common guide, then:

```powershell
python tools/build_recomp_chunks.py --jobs 2
python tools/link_noble_archimedes.py
Remove-Item Env:PS2_VU_BACKEND -ErrorAction SilentlyContinue
$env:PS2_GS_BACKEND = "cpu"
.\NobleArchimedes.exe
```

The output filename is the same as profile A; keep clones separate when recording hashes/results. CPU GS is useful for graphics/state regressions and relevant CPU-only tests. Do not use its performance as evidence that the GPU configuration meets or misses its target. You may also select `cpu` at runtime in a GPU-capable build for a diagnostic comparison; that does not remove GPU libraries from that executable.

## C. Hybrid with actual PCSX2 GS

This profile has two toolchains: **MinGW** for the host/runtime and **MSVC 14.40.33807 + Windows SDK 10.0.22621.0** for the GS adapter. It also needs CMake/Ninja, 7-Zip, a D3D11 device and official PCSX2 dependencies. `tools/pcsx2_gs/build.py` has explicit toolchain paths; inspect/adapt its `VC`, `SDK` and `SDKVER` constants for your installation. Do not reuse MinGW objects in the MSVC DLL.

In a separate checkout, restore the runtime patch and build the adapter:

```powershell
git clone --no-checkout https://github.com/PCSX2/pcsx2.git output/reference_sources/pcsx2
git -C output/reference_sources/pcsx2 checkout --detach 646df006a4688063e56c0826e7ea4b8bb0c112c4
git -C output/reference_sources/pcsx2 submodule update --init --recursive
python tools/pcsx2_gs/build.py toolchain
python tools/pcsx2_gs/bootstrap.py
python tools/pcsx2_gs/build.py consumer
```

Expected module: `output/fps60/pcsx2_gs_consumer_v1/bin/noble_pcsx2_gs.dll`. Keep package-provided dependency DLLs beside it. Bootstrap checks the downloaded official release asset's SHA256, but the asset currently resolves at run time; record its digest with build reports. No dependency binaries or upstream resources are shipped in this repository.

Configure the MinGW host with both renderer implementations so the saved choice can select either on restart:

```powershell
python tools/PS2Recomp/ps2xRuntime/scripts/fetch_parallel_gs.py
cmake -S tools/PS2Recomp -B tools/PS2Recomp/build -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_COMPILER=gcc -DCMAKE_CXX_COMPILER=g++ -DPS2X_BUILD_STUDIO=OFF -DPS2X_BUILD_TEST=OFF -DPS2X_ENABLE_PGS=ON -DPS2X_ENABLE_PCSX2_GS=ON
cmake --build tools/PS2Recomp/build --target ps2_recomp ps2_runtime ps2_iop --parallel 2
```

Generate local guest C++ using the common guide. Build chunks, then explicitly compile the host with the bridge definition; the manual builder does not inherit CMake's public definitions:

```powershell
python tools/build_recomp_chunks.py --jobs 2
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
Remove-Item Env:PS2_VU_BACKEND -ErrorAction SilentlyContinue
$env:PS2_PCSX2_GS_ADAPTER = (Resolve-Path output/fps60/pcsx2_gs_consumer_v1/bin/noble_pcsx2_gs.dll).Path
$env:PS2_PCSX2_GS_RESOURCES = (Resolve-Path output/reference_sources/pcsx2/bin/resources).Path
$env:PS2_GS_BACKEND = "pcsx2"
.\NobleArchimedes.exe
```

Repeat the explicit host-definition step after future `build_recomp_chunks.py` runs, which otherwise rebuild host objects with default flags. This manual step is a useful build-system contribution opportunity.

After building the real adapter, its synthetic integration checks are available separately:

```powershell
python tools/pcsx2_gs/test_real_module.py
```

These open the actual D3D11 GS module; they are not a gameplay benchmark. EE/VU/gameplay remain in this project's runtime, and no PCSX2 VM/BIOS is started. ABI, resource or dependency failures must be fixed rather than reported as a successful PCSX2 run. For implementation boundaries see [the adapter README](../tools/pcsx2_gs/README.md).

## D. Native VU optimized development build: availability boundary

Development benchmarks used a separately built `noble_vu_jit.dll`, including native VU Program 4/Program 3 work. Game-derived translations and its private build/research tooling are excluded. There is currently **no complete public command sequence to regenerate and rebuild that exact module**. Installing stock Play! or PCSX2 is not a replacement for this ABI.

The generic loader contract is published in the runtime patch as `ps2xRuntime/src/lib/vu/ps2_vu1_native.h`. A future reproducible contributor path must generate translations locally from the user's game, build a module with matching version/state size and exports, preserve the runtime's VU state/cycle/packet contract, and pass correctness and cost gates. Publish generators, generic helpers and synthetic tests; keep generated game implementations local.

Only if you already have an independently built, compatible module beside the executable should you select it:

```powershell
$env:PS2_VU_BACKEND = "play"
.\NobleArchimedes.exe
```

Return to the public generic VU default by removing that environment variable. The historical selector name `play` does not certify a particular translation, module hash or correctness level. Report the actual module SHA256 when comparing performance.

## E. Full native engine-seam GPU research

There is no completed public target, production selector or build recipe for this path. The private experiments validated pieces of skinning/projection and state handling, not a complete integrated native renderer. Selecting `pgs` or enabling the PCSX2 bridge does not activate those experiments.

Contributors can work on the [remaining dependency and integration gates](PROJECT_STATUS.md) using original generic implementations, synthetic fixtures and tools that derive game-specific inputs locally. A reproducible source-only research harness is welcome. A complete implementation needs ordered normals/extrusion/projection/clipping/cache effects, preserved consumed VU/parser state, a guarded fallback and inclusive cost/gameplay validation before a launch recipe can be offered.

## Rebuilds, troubleshooting and evidence

- **Host/UI-only changes:** run the chunk/host helper, then relink. For hybrid, repeat the explicit host-definition step above.
- **Runtime changes:** rebuild `ps2_runtime`/`ps2_iop` as appropriate, refresh host/chunks if headers changed, then relink.
- **Compiler/configuration changes:** regenerate guest sources locally, refresh generated entries/registration as in the common guide, rebuild chunks and relink. Keep the unmodified input and tool version identifiable.
- **Missing imports:** inspect the executable/module dependencies and supply authorized local DLLs. Do not mix compiler-runtime versions blindly.
- **Missing GPU link archive or stale configuration:** use the matching dedicated checkout/build tree; the helpers do not support arbitrary build directories yet.
- **Performance reports:** record commit, profile, compiler/dependency/module identities, hardware, load, scene/input, actual guest updates and fresh images over stated intervals, and correctness checks. Disable heavy tracing for the timed run.

Build failures and incomplete clean setup are useful contribution targets. State exactly which step failed; do not present untested command sequences or a window FPS counter as a successful port. See [CONTRIBUTING.md](../CONTRIBUTING.md) to submit findings or fixes.
