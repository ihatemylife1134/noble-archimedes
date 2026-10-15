# Noble Archimedes - Castlevania CoD Recomp

An experimental Windows x64 recompilation project for **Castlevania: Curse of Darkness**, USA PlayStation 2 release, **SLUS-21168**. The goal is native gameplay at 58–60 updates per second while preserving the game's behavior.

**Status, 2026-10-15: playable development builds exist, with measured framerates reaching ~53.0 FPS in gameplay transitions under Stage A scheduler optimization and native VIF1 worker (advancing past previous 20.5–26.4 FPS and 31.50 FPS baselines toward the 58–60 FPS target).** Release notes, setup instructions, and limitations are recorded in the [changelog](CHANGELOG.md). Alpha 0.2.0 release artifacts are available on GitHub.

No game ISO, executable, assets, translated game implementation, game microcode, captures, saves, or compiled binaries are distributed here. Supply your own lawfully obtained game copy and generate guest code locally. See [BUILDING.md](BUILDING.md) for the workflow and its limitations.

## Why “Noble Archimedes”?

The name is a thematic codename, not a Castlevania character or official subtitle. “Archimedes” evokes engineering, mechanics and discovering how a complicated machine works; “Noble” expresses the preservation aim. The Castlevania connection is rebuilding and forging: Hector's Devil Forgery provides a metaphor for assembling a new host around the original game's behavior. The owner confirmed that the connection is thematic; this is an interpretation of the name, not a claim about its historical origin or game lore. Konami's [official game page](https://www.konami.com/games/castlevania/us/en-us/page/history_2005_ps2) describes Devil Forgery and the Innocent Devils.

## Architecture and renderer paths

The EE executable is translated locally from MIPS to C++ and compiled into host machine code. The runtime supplies scheduling, memory, VIF/GIF, controllers, storage and other compatibility services. Native CPU execution does not imply that all PS2 hardware semantics have disappeared.

| Path | CPU / VU | Graphics | Status |
| --- | --- | --- | --- |
| Native default | Recompiled EE; generic VU compatibility execution in this public snapshot, with native VU optimizations developed separately | Vulkan paraLLEl-GS; CPU GS for diagnostics | Working development path; gameplay target unmet |
| Hybrid — PCSX2 GS | This project's EE/VU and scheduling stay in control | Actual PCSX2 GS through a C-ABI DLL, initially surfaceless D3D11 | Adapter and bridge implemented; no demonstrated 60 FPS gameplay solution |
| Full native engine seam, intended destination | Recompiled gameplay plus owned GPU mesh processing, preserving consumed VU effects | Native GPU processing integrated with a coherent renderer | Component math validated privately; complete gameplay replacement unfinished |

Hybrid mode does not run the whole PCSX2 emulator. It is a recompilation with an emulated GS renderer. The default also retains GS hardware compatibility through paraLLEl-GS; “Native” is a UI label, not a claim that every device has become a conventional PC engine.

## What “near 60 FPS” actually means here

Host presentation pacing was improved: ordinary wake-up jitter remains on the scheduled VBlank phase, while missed-period behavior and virtual cycle accounting are retained. A Windows timer-resolution helper also addresses the platform ignoring the requested resolution. VU state, ordered packets and guest completion remain correctness requirements.

| Latest recorded native gameplay run | Result |
| --- | ---: |
| Gameplay updates | 1,566 / 43.703 seconds = **35.83/s** |
| Fresh presented images | 3,215 / 55.016 seconds = **58.44/s** |
| Presentation requests / repeated images | 3,301 / 86 |
| Reported capacity, stale or age drops | 0 |
| Exit / movement check | Normal exit; ordinary movement observed |

The newest recovery run used the native VIF1 worker, a VU-correct experimental module and an EE scheduler that skips proven-empty event drains and retains event/deadline scratch capacity. Its protected gameplay state stayed `[4, 10, 3, 1]` from the first to last sample; process use was 1.916 CPU cores and host busy time was 19.86%. The run's prior-build paired control was interrupted, so **31.50/s is a measured candidate result, not a proven isolated speedup**. Scheduler concurrency/deadline and VIF1 worker restore/GIF-order fixtures passed.

A later same-scene pipeline ablation under heavier accepted machine load measured 13.00 updates/s synchronously and 20.55/s with the VIF1 worker. Conservative VU dead-flag elimination further improved performance to 26.38 updates/s (cutting VU worker CPU time from 11.78s to 7.33s). The subsequent Stage A EE scheduler overhaul (introducing an inner quantum execution loop and a 64K direct-mapped L1 block cache) eliminated ~930,000 scheduler context roundtrips per second, leaping to **~53.0 FPS** (912 frames in 17.2s). See [the detailed pipeline documentation](docs/PROJECT_STATUS.md).

The 35.83 and 58.44 measurements above use different windows; do not divide one counter by the other's interval. The user accepted existing background load. Captures, executables, game inputs and the game-derived optimized VU module are excluded. Earlier gameplay candidates varied around 43–45 FPS but did not establish the current VU-correct configuration. A full-PCSX2 reference recorded 59.91 guest updates/s, but does not establish GS-only speed or a controlled comparison of identical builds and load.

**Near-60 presentation has been observed. Sustained 58–60 FPS gameplay is actively within reach at ~53 FPS.** See [detailed status and remaining work](docs/PROJECT_STATUS.md).

## Build and start playing

This is a developer workflow. Established tools: Windows x64, MinGW-w64 GCC/G++ 15.2, Python 3.12, CMake/Ninja and a Vulkan driver. The optional GS DLL uses a separate MSVC toolchain.

1. Clone recursively and apply the supplied runtime patch.
2. Supply your own USA game ISO and extract `SLUS_211.68` locally.
3. Build PS2Recomp and generate guest C++ from the local ELF/configuration.
4. Build the runtime, generated chunks and host; link `NobleArchimedes.exe`. The native VIF1 worker is an opt-in runtime path through `PS2_NATIVE_VIF1_WORKER=1`.
5. Keep the local ISO, `extracted/SLUS_211.68` and locally acquired dependency DLLs beside the executable, then launch it.

Commands, dependencies, settings and unresolved clean-setup steps are in [BUILDING.md](BUILDING.md). **A clean public checkout has not yet been qualified end-to-end through gameplay.** Private optimized VU modules and game-specific GPU translations are excluded; neither the 31.50 recovery result nor the 35.83/58.44 ledger result is a benchmark of a fresh public build.

For individual configurations, see [build variants](docs/BUILD_VARIANTS.md): native Vulkan, CPU diagnostics, PCSX2 GS hybrid, and the availability limits of native VU/engine-seam research.

## Fork it and help build the port

**Forks, experiments and pull requests are welcome.** Help us make the public build reproducible, preserve VU correctness and reach real 58–60 FPS gameplay. Build-system fixes, documentation, synthetic tests and carefully measured performance work all move the project forward; you do not need to solve the entire renderer to contribute.

Start with [CONTRIBUTING.md](CONTRIBUTING.md) for a fork-and-branch workflow, useful first tasks, runtime-patch instructions and what to include in a performance report. If a clean build fails, a precise report is useful too. Share source changes and aggregate measurements while keeping game inputs and generated game implementations local.

Keyboard defaults: WASD movement; arrows D-pad/menu; J/left mouse attack; K/right mouse special; Space jump; E/L action; Shift guard; Enter/Escape Start/menu; M map; V experimental camera toggle. Supported controllers can be used. Camera modes, sound, movies, saves and broader game coverage still need validation; reaching the courtyard does not prove the entire game works.

The overlay saves `Native` or `Hybrid — PCSX2 GS`; restart to apply. Settings: `%APPDATA%/NobleArchimedes/renderer.cfg`, or `noble-renderer.cfg` when APPDATA is unavailable. `PS2_GS_BACKEND=pgs`, `cpu`, or `pcsx2` overrides the choice. Missing PCSX2 support reports an error.

## What is missing for native 58–60 FPS?

1. Complete skinning → triangle normals → extrusion → projection → clipping → packet/cache writes. Later launches consume earlier writes; isolated fresh-mesh inputs are insufficient.
2. Preserve consumed VU registers/flags and pipelines, Q/P timing, data memory, parser state, cycles, packet ordering and exactly-once completion.
3. Integrate the complete GPU job with admission guards and a correct fallback. Small GPU math tests are not installed gameplay replacements.
4. Beat CPU cost including ownership, packing/upload, dispatch, synchronization, readback/state publication and renderer interoperation. Previous affine-only and packet-copy experiments failed this test.
5. Benchmark moving gameplay again with both guest updates and fresh images at 58–60/s, then broaden scene and whole-game coverage.

PCSX2 accelerates more than rasterization: CPU/VU execution, scheduling and rendering work together. A GS-only swap leaves our VIF/VU work and ordering waits in the critical path. OpenGOAL demonstrates a mature game-specific native engine; its engine code is not a transferable replacement for this game's different pipeline.

## Publication and dependencies

This repository starts with a **new sanitized Git history** containing host/glue, build/generation tools, dependency references and licensed runtime modifications. Generated game C++, literal microcode/GPU translations, research captures and binaries stay local. The exploratory research directory is not bulk-published.

PS2Recomp is pinned at `75d729ce40d7eed9649fd4bb05628dee520f3d0c`; runtime modifications are supplied as a patch. PCSX2 GS builds against `646df006a4688063e56c0826e7ea4b8bb0c112c4`. See [third-party notices](THIRD_PARTY_NOTICES.md) and [publication scope](docs/PUBLICATION.md). Upstream licenses continue to apply. This snapshot assigns no new blanket license or rights to the game.

Independent fan research, unaffiliated with Konami, Sony, PCSX2 or other upstream projects. Castlevania and its content belong to their respective rights holders.
