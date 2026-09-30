# Performance investigation notes (2026-09-27)

Goal: 60 fps (60 guest VBlanks per wall second). Baseline after the render fix: 0.11 VBlanks/s.
Measured with `output/diag_perf/run_capture_nul.ps1` (stdout/stderr drained in memory, host profile to
`PS2_HOST_PROFILE_FILE`) and the `[host-profile]` line printed every 5 s by `runtime/host_profile.h`.

Host: Ryzen 7 2700X (8C/16T). Windows was on the **Power saver** plan during every measurement below;
the CPU ran at ~2.2 GHz instead of 3.7-4.3 GHz. All numbers are relative to that clock.

## Root causes found and fixed (in order)

| # | Cause | Evidence | Fix | VBlanks/s after |
|---|-------|----------|-----|-----------------|
| 1 | EE thread blocked on synchronous log writes (stderr unbuffered, per-event diagnostics; one `WriteFile` stalled for seconds) | EE CPU 2.7 s / 5 s wall; 7/10 stack samples in `ZwWriteFile` | `PS2X_ENABLE_AGRESSIVE_LOGS=OFF`, hot unbounded prints behind `PS2_IF_AGRESSIVE_LOGS`, non-blocking stdio relay `ps2_async_stdio.cpp` (test `async_stdio_relay_test.cpp`, red/green) | ~4 |
| 2 | GS software rasterizer ran synchronously on the EE thread (~10 ms per 256x256 sprite) | `draw` ~3.7 s / 5 s on the EE thread | Row-band worker pool in `GSCpuBackend` (8 workers), exclusive steps for uploads/CLUT/flush, page-level hazard tracking; bit-exact oracle `gs_raster_diff.cpp` | ~4.4 (EE then spin-bound) |
| 3 | IOP emulator advanced on every 32-cycle checkpoint | `iopAdvance` up to 2 s / 5 s, ~1 us fixed cost per call | `EeScheduler::kIopBatchEeCycles = 2048` | (included above) |
| 4 | Missing DMA-allocator spin fast-forward for `sub_004205E8` (0x420628) and the second `sub_00420450` loop (0x420528) | 100% of checkpoint PC samples at 0x420628/0x75d440/0x75d460 | added both loop heads to `isQueueSpin` | ~11 |
| 5 | SPU2 core STATX DMA-busy bit (0x80) never cleared: LIBSD's init waited its full timeout (3841 x 1800-instruction delay loop) on every reset | IOP PC samples 100% in delay loop 0x47DC8; caller polls 0xBF900344/0x744 & 0x7FF | `IopMemory::completeDma` clears the bit when the SPU2 DMA completes (test in `ps2xIOP/tests/iop_emulator_tests.cpp`, red/green) | ~12.5 (IOP 2.1 s -> 8 ms / 5 s) |
| 6 | Host UI thread drained the whole GS queue under the backend lock every VBlank (`Sync(Presentation)`) | `gsDrainSync` ~52 ms per frame; EE blocked in `Submit` | ordered `PresentSnapshot` command + conversion on the UI thread (`GSCpuBackend::EnableAsyncPresentation`, enabled by `PS2Runtime::run`) | ~14-17 |
| 7 | ~7200 full worker barriers per 5 s (flush, CLUT, upload) around only ~3700 draws | command counters | per-page last-read/last-write tracking; per-worker TEXFLUSH and CLUT; direct producer uploads to idle pages; write-after-read hazards now ordered (new oracle mode `pingpong`, mutation-tested) | ~20 |
| 8 | Per-pixel calls not inlined | replay benchmark 156 ns/pixel | `always_inline` on WritePixel/SampleTexture/LookupCLUT (oracle identical) | benchmark 126 ns/pixel |

In progress: guest chunks at `-O2 -fno-strict-aliasing -fwrapv` (were `-O0`; register helpers such as
`Ps2SetGprLow64` were ~15% of EE time as real calls), `EeScheduler::publishSnapshotThrottled` (debug
snapshot was ~8% of EE time plus heap churn).

## Validation

- Rasterizer oracle: `output/diag_perf/run_raster_matrix.sh <cases> <seeds>` builds
  `ps2xRuntime/tests/gs_raster_diff.cpp` against the pre-change snapshot in `output/diag_perf/reference_gs`
  and the working tree, and compares a 64-bit VRAM hash per case (modes single, disjoint, sequence,
  pingpong; 1/2/3/8/16 workers). Last full run: 32/32 configurations identical (64,096 cases).
- `ps2x_tests`: 432/437 (5 pre-existing scheduler/RPC failures) before the GS threading work; rerun pending.
- IOP suites (emulator, import, compatibility, import-version) pass.

## Tools

- `PS2_RIP_SAMPLES=<file>` (EE thread) and `PS2_RIP_SAMPLES_GS0=<file>` (GS worker 0): RIP sampler,
  symbolize with `output/diag_perf/symbolize_samples.py <exe> <file>`.
- `ps2xRuntime/tests/gs_sprite_raster_bench.cpp`: replays captured draws; `output/diag_perf/line_profile.py`
  gives a source-line histogram for a `-g` build.
- `PS2_GS_THREADS=N` selects GS workers (0/1 = synchronous reference path).
