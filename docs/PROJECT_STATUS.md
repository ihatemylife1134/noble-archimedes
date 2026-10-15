# Project status — 2026-10-15

## Verified scope and the open target

58–60 FPS gameplay remains unachieved. The newest VU-correct recovery run measured **31.5009 guest updates/s**: 1,232 updates over 39.110 seconds, with the protected gameplay state unchanged at `[4, 10, 3, 1]`. Process use was 1.916 CPU cores and host busy time was 19.86%. Its prior-build paired control was interrupted, so this is a candidate measurement rather than proof of the isolated scheduler delta. The older private ledger maximum remains **35.8328 guest updates/s; 58.4375 fresh images/s** under a different build/window. Supporting executables, game inputs and captures are excluded.

The project has an EE recompilation host, controls, overlay, local ISO filesystem, compatibility runtime and Vulkan GS integration. A saved renderer choice and actual PCSX2 GS-only adapter exist. Native VU optimizations and smaller GPU math components have been qualified privately. The complete engine-seam GPU path has not been admitted into gameplay.

## What helped

- The native VIF1 worker moves VIF/VU execution off the saturated EE executor while retaining explicit fencing, owner-state restoration, packet ordering and exactly-once completion.
- A scheduler no-work certificate skips timer/DMA/event bookkeeping when existing atomics prove that no work is pending. Reusing executor-local event and deadline containers removed recurring heap churn. The recovered candidate reached 31.5009 updates/s; an isolated paired result still needs to be rerun.
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
