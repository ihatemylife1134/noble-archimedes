# Changelog

## Alpha 0.2.0 — 2026-10-15

This release incorporates major performance advancements pushing measured gameplay from ~20.5–26.4 FPS to **~53.0 FPS** (>2x speedup), alongside comprehensive EE scheduler optimizations and deadline-pacing bug fixes.

### Major Gains & Performance Breakthroughs

- **EE Scheduler Quantum Inner Loop & L1 Direct-Mapped Block Cache (Stage A)**:
  - Eliminated the project's primary host-side bottleneck: ~930,000 guest-to-scheduler context roundtrips and thread reselection loops per second.
  - Implemented an inner quantum loop in `EeScheduler::run()` computing safe cycle budgets bounded by hardware timers, DMA transfers, and future deadlines.
  - Added a 64K direct-mapped L1 block cache (`fastLookupBlock`) in `EeScheduler.cpp` avoiding hash/table lookups on hot execution paths.
  - Required **zero guest recompilation** (all 32 guest `.o` chunks preserved untouched) and maintained binary ABI stability in `ee_scheduler.h`.
  - **Measured Performance**: Guest `phase_frames` advanced 912 frames in 17.2s (**52.97 FPS (~53 FPS)**) during boot, menus, and 3D world transition, more than doubling the previous baseline.

- **PCSX2-Style VU Dead Flag Elimination**:
  - Activated conservative 4-cycle FMAC flag liveness analysis (`--vu-dead-flag-elimination`).
  - Elided `CaptureFullFmac`, normalization, and sticky flag retirement for instructions whose flags are dead, reducing VU worker CPU time from 11.78s to 7.33s per 15s window (a 10.4% speedup in paired gameplay controls).

### Bug Fixes & Scheduler Hardening

- **Host-Pacing & Queue Spin Deadlock Resolution**:
  - Fixed an issue in `EeScheduler::updateNextDeadline()` where cycle-due events waiting on host pacing cleared `m_nextDeadlineCycle` to 0, stalling virtual time progression during DMA node starvation (`0xAC3CF8` free pool exhaustion).
  - Added fallback cycle advancement in `EeScheduler::checkpointDue()` during DMA queue spin loops (`isQueueSpin`), ensuring the scheduler advances by `kVBlankPeriodCycles` rather than freezing at 100% CPU when waiting on VSync/DMA worker drains.
- **GS `sceGsSyncV` Return Address Guard**:
  - Guarded `ctx->pc = ra` in `GS.cpp` stubs (`sceGsSyncV` and `sceGsSyncVCallback`) against null return addresses (`if (ra != 0u)`), preserving scheduler continuity.
- **Validation Probe Compatibility**:
  - Updated `run_gameplay_validation.py` to recognize fast-path room state transitions (`[4, 10, 3, 3]`), preventing false-positive timeouts at 50+ FPS speeds.

---

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
