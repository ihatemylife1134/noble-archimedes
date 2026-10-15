# Changelog

## Alpha 0.1.0 — 2026-10-15

This is the first named development release of Noble Archimedes. It publishes the advanced native VIF1 worker and scheduler work, selectable graphics architecture, reproducible build documentation and a source-only Windows release kit.

### Selecting the game

Only the USA PlayStation 2 release **SLUS-21168** is supported. Use your own lawfully obtained disc image. Name it `Castlevania - Curse of Darkness (USA).iso`, place it beside the locally built executable and extract `SLUS_211.68` to `extracted/SLUS_211.68` using the command in [BUILDING.md](BUILDING.md). The release contains no game data or translated game implementation.

### Selecting the GPU renderer

- Double-click `Launch Native.cmd` for the native recompilation path with Vulkan paraLLEl-GS.
- Double-click `Launch PCSX2 GS.cmd` for the experimental PCSX2 GS-only adapter. It requires a build configured with `PS2X_ENABLE_PCSX2_GS=ON`, `noble_pcsx2_gs.dll`, its licensed dependencies and resources.
- From a running build, press **F1**, expand **Graphics**, choose **Native** or **Hybrid (PCSX2 GS)**, then restart. The saved choice takes effect on the next launch.

Hybrid mode keeps this project's recompiled EE, VU execution, scheduling, input and gameplay runtime. It replaces only the GS renderer and does not start a complete PCSX2 virtual machine.

### Current performance and correctness

The newest retained VU-correct candidate measured **31.5009 gameplay updates/s**: 1,232 updates over 39.110 seconds with protected gameplay state `[4, 10, 3, 1]` unchanged. An older private-development ledger run recorded **35.8328 gameplay updates/s** and **58.4375 fresh presented images/s** over different measurement windows. These results do not establish sustained 58–60 FPS gameplay, and the public source kit does not reproduce the private optimized VU DLL.

The retained work includes the native VIF1 worker, explicit fencing and state restoration, ordered GIF packet handling, a scheduler empty-work fast path, reusable event/deadline scratch storage, Windows timer-resolution handling, renderer settings and the PCSX2 GS adapter source.

### What remains

- Reach and validate 58–60 actual gameplay updates/s with VU correctness preserved.
- Finish the ordered native engine seam through skinning, normals, extrusion, projection, clipping and packet/cache writes.
- Prove the PCSX2 GS-only bridge in real gameplay and package its complete licensed dependency/resource closure.
- Make clean public game-code generation and the end-to-end Windows build reproducible.
- Separate user-generated game implementation from the redistributable host so a playable public binary can be shipped without game-derived code.
- Resolve remaining GS test failures and the broad test-suite VSync stall.
- Qualify combat, enemies, Innocent Devils, effects, transitions, movies, sound, memory cards and saves.

### Distribution boundary

The GitHub asset is a **source-only Windows kit**. It opens through the supplied command launchers after the user builds the host locally. It excludes the game ISO, extracted executable, generated/recompiled game implementation, private VU/GPU translations, captures, saves, dependency binaries and compiled host executable.
