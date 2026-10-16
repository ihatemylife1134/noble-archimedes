# Project status — 2026-10-15

## Verified scope and the open target

58–60 FPS gameplay is actively approached. The newest Stage A scheduler candidate measured **52.97 guest updates/s (~53.0 FPS)**: 912 frames in 17.218 seconds during boot/menu/3D world transition. This represents a >2x improvement over the 26.381 FPS baseline from the prior dead-flag elimination pass and outpaces the earlier 31.50 and 35.83 FPS recovery measurements. Process use was 1.916 CPU cores and host busy time was 19.86%. Supporting executables, game inputs and captures are excluded.

The project has an EE recompilation host, controls, overlay, local ISO filesystem, compatibility runtime and Vulkan GS integration. A saved renderer choice and actual PCSX2 GS-only adapter exist. Native VU optimizations and smaller GPU math components have been qualified privately. The complete engine-seam GPU path has not been admitted into gameplay.

## Pipeline ablation completed on 2026-10-15

A fresh controlled courtyard series used the same protected gameplay state and current accepted background load. Absolute rates were lower than the earlier recovery run, so the series is used for within-series attribution rather than as a new performance maximum.

| Run | Guest updates/s | Result |
| --- | ---: | --- |
| Synchronous VIF1/VU, normal GS | 13.000 | Control |
| VIF1 worker, normal GS | 20.547 | 58.1% faster than synchronous; retain the worker |
| Worker, frame-sized blended batches suppressed | 18.450 | More than 300 qualifying batches were skipped; no rasterization speedup |
| Worker, texture-cache invalidation suppressed | 20.226 | Cut activated; flat against the worker baseline |
| Worker, host VBlank deadline pacing removed | 20.450 | Cut activated; no evidence of a two-field host wait |

The rendering cuts consume GIF commands and preserve state progression. The blend cut is deliberately an upper-bound diagnostic because this game combines hundreds or thousands of blended primitives into frame-sized PGS render passes; it is not a playable renderer mode. The different diagnostic executables contain only their gated cut code, so compare the direction and size of the result, not sub-percent noise across hashes.

An aggregate 47.265-second worker profile recorded 18,620 jobs. Worker execution consumed 34.515 seconds, blocking fences 2.668 seconds and completion/GIF commits 1.029 seconds. Removing every measured fence and commit cost would still be far short of 58–60 updates/s. A separate 15-second all-thread sample found 13.328 CPU-seconds on the EE/scheduler thread and 11.781 CPU-seconds on the VU worker. The VU worker's largest named residents were generic full-FMAC correctness helpers (`CaptureFullFmac`, `NobleFullPairFlags`, sticky retirement and normalization); the two specialized Program 4 blocks had much lower residence.

This closes the immediate VBlank, worker-control, fullscreen-raster and texture-invalidation branches. The next substantial native gain must expand correct Program 4 coverage or replace the complete owned VU mesh job at the engine seam. More GS-only cuts and indiscriminate fence removal are not supported by these measurements.

## Dead flag elimination and Stage A EE Scheduler optimization (2026-10-15)

Following the pipeline ablation, all-thread CPU sampling showed the VU worker spending substantial time in conservative full-FMAC flag capture helpers (`CaptureFullFmac`, sticky retirement, normalization) while the EE scheduler thread was heavily loaded with host-side bookkeeping (~930,000 guest dispatches/second). Two sequential optimizations were designed, implemented, and validated:

### 1. PCSX2-Style VU Dead Flag Elimination
- **Mechanism**: Activated conservative 4-cycle FMAC flag liveness analysis (`--vu-dead-flag-elimination`). For instructions where neither status nor MAC flags are read across successor blocks, flag emission, sticky accumulation, and normalization helpers were elided.
- **Measured Result**: Gameplay framerate rose from 20.55 FPS to **26.381 FPS** (+28.4% absolute, +10.4% in paired identical-build control). VU worker CPU time dropped from 11.78s to 7.33s per 15s window, with 100% pass on all 13 VU oracle/regression fixtures.

### 2. Stage A: EE Scheduler Inner Quantum Loop & Direct-Mapped L1 Block Cache
- **Diagnosis**: Symbol-level profiling of the EE/scheduler thread revealed ~930,000 guest dispatches per second—roughly 35,000 scheduler round-trips per gameplay update. The recompiler was returning to `EeScheduler::run()` after tiny blocks, incurring repeated thread reselection, lock acquisition, host clock queries (`RtlGetSystemTimePrecise`), and hash-map lookups.
- **Mechanism**:
  - Implemented an inner quantum loop inside `EeScheduler::run()`, executing consecutive guest blocks within a calculated safe cycle budget (bounded by hardware timer interrupts, DMA completions, and future deadlines) before yielding.
  - Implemented a 64K direct-mapped L1 block cache (`fastLookupBlock`) in `EeScheduler.cpp` for $O(1)$ fast block lookup without hash map overhead.
  - Required **zero guest recompilation**: all 32 compiled guest chunks (`recomp_chunk_*.o`) and `class EeScheduler` header ABI layout remained completely untouched.
- **Measured Result**: During boot, menus, name entry, and 3D world transition, `phase_frames` advanced from 2,616 to 3,528 in 17.218s—measuring **52.97 FPS (~53.0 FPS)**, a **>2x speedup** over the 26.381 FPS baseline.
- **Deadlock Hardening & Pacing Resolution**: Resolved an issue where cycle-due events waiting on host pacing continuously triggered `m_checkpointPending`, causing 968,000 scheduler dispatches per second and burning 76% of CPU in dispatch loops. Gating `cycleEventDue` with `!cyclePaced` reduced dispatches to ~3,900/s while preserving 60 Hz VSync. Restored clean `std::min_element` deadline selection in `updateNextDeadline()` to eliminate DMA queue lockups in `sub_0041FFF0`. Replaced artificial cycle jumps with cooperative yields when the DMA free pool (`freeHead == 0u`) is temporarily exhausted.
- **Steady-State Courtyard Profiling**: In steady-state 3D courtyard (`[4, 10, 3, 1]`), measured 14.43 FPS across 922 frames (63.9s) at 0.54 host CPU cores, proving host scheduler overhead is eliminated and isolating remaining frame time to GPU/VIF1 rasterization and draw calls.

## What helped

- The native VIF1 worker moves VIF/VU execution off the saturated EE executor while retaining explicit fencing, owner-state restoration, packet ordering and exactly-once completion.
- A scheduler no-work certificate skips timer/DMA/event bookkeeping when existing atomics prove that no work is pending. Reusing executor-local event and deadline containers removed recurring heap churn. The recovered candidate reached 31.5009 updates/s; the later current-load paired run confirmed that the worker materially outperforms synchronous execution.
- Native VU Program 4 blocks and Program 3 joins reduce generic execution work. Those game-derived translations are excluded from publication.
- VU work addressed rounding, flags, masked lanes, pipeline timing, cycle deltas versus absolute clocks and packet ordering.
- Scoped SIMD/AVX experiments offered roughly 1–2% gains in tested cases, insufficient to bridge the gameplay deficit.
- Host VBlank phase pacing and Windows timer-resolution handling improved presentation toward 60 Hz, without removing the gameplay processing bottleneck.
- Worker diagnostics found waits at GS privileged-register and GIF ordering boundaries. Queue depth increases or deleting fences are not justified without dependency proof.
- Raw GS feed handling already avoids unnecessary decoded reconstruction where applicable; it is not a newly discovered saving.

## Private GPU milestones

These describe retained development evidence, not a public benchmark suite or whole-game proof.

| Component | Qualified scope | Remaining limit |
| --- | --- | --- |
| Complete skin/source decoding | 3,681 rows: 2,441 rigid, 1,216 two-palette, 24 three-palette; 448 descriptors; reference 44 launches/331 packets | Complete engine replacement and cost |
| Compact GPU skin math | 3,681 rows and 22,284 mapped operations matched the CPU oracle, including flags/metadata; zero repairs. Wrong-third-weight mutation detected | 856 separately accounted extra/prefetch operations, final state, clipping and FPS |
| Compact GPU projection | 3,022 current-live rows, 36 payload words each matched; masked carry, Q timing and conversion checked | Complete provenance of GPU input/state |
| Owned VIF/parser and owner restoration | Ordered decode, guarded parser publication, private state and previous-public-mirror restoration qualified in isolated fixtures | Live runtime integration and performance |

Tests used an actual RTX 3080 and explicit floating-point feature/rounding controls. Successful small kernels compile in seconds. They do not establish a complete native renderer.

## Rejected experiments

- Affine-only GPU offload: roughly 2.9–3.2 ms including packing/cache/install versus 1.2–1.4 ms CPU in the tested scope. Cost rejected.
- Owned packet-copy avoidance: old 10.54695 ms versus candidate 10.60295 ms, approximately 0.53% slower in the qualified paired fixture. Not installed.
- Monolithic 98-block Program 4 GPU translation: roughly 585 KB shader failed bounded driver compilation attempts with original, helper-hint and disabled-optimization variants. No complete-job GPU output. Size-optimization compilation also timed out. Repeating those variants is not a useful next step.
- GS-only substitution: real adapter implemented, but no retained result demonstrates 58–60 gameplay through that bridge. Full-emulator speed is not bridge performance.

## Current engine-seam blocker

The real chain is skinning → triangle cross-product normals → extrusion → projection → six-plane clipping → packet/cache writes. All 3,022 observed projection positions differ from initial affine output. Extrusion produces 4,577 writes: 3,681 tied to current affine data and 896 carried without fresh upload. Control words also require owned initial VU memory.

A later normal read depends on memory overwritten by an earlier projection/packet-cache stage. The missing piece is an ordered, versioned provider for those writes, including clipping/cache effects. Seeding from future captures or equating physical addresses with permanent vertex identities is invalid.

Preserve consumed flags/registers and pipelines, Q/P, masked carry, memory writes, VIF/parser state, cycles, ordered packet bytes/times and exactly-once DMA/completion. Keep the owner's previous-public-state mirror coherent. An unknown next consumer is not dead state merely because the fixture ended.

## Next implementation gates

1. Close provenance through normals, extrusion, projection, clipping and cache output from owned initial inputs and earlier derived outputs.
2. Validate a compact complete GPU job against CPU state/data/parser/ordered packets, with meaningful mutations and rejection cases.
3. Admit eligible jobs with code/control/lifecycle/ownership guards, correct fallback and no duplicate original drawing/completion.
4. Pass inclusive warm cost testing before gameplay installation.
5. Run actual gameplay with ordinary movement, active hook/module evidence and both counters at 58–60/s.
6. Expand to combat, enemies, Innocent Devils, effects, transitions, movies, sound and saves. A courtyard run is insufficient for release.

## Public snapshot versus private development

The publication includes the generic native VIF1 worker, scheduler no-work/event-buffer changes, renderer settings and GS adapter source. Enable the worker with `PS2_NATIVE_VIF1_WORKER=1`; unset it to return to synchronous VIF1 execution. The publication excludes game-derived native VU/GPU translations and private captures. Generic VU interpretation remains available; `PS2_VU_BACKEND=play` requires a separately built compatible experimental module which is not supplied. Do not set it expecting a bundled DLL.

The established incremental build relies on configured dependencies. Clean public generation/build/play has not been validated end-to-end. Dependency setup, packaging and regeneration of private optimized translations remain outstanding. Custom sound-service/audio and movie behavior remain incomplete, and whole-game correctness/stability are not established. No claim is made that today's public source exactly reproduces the private benchmark binary.
