# Handoff: Castlevania: Curse of Darkness (SLUS-21168) PS2 static recomp — "Noble Archimedes"

Snapshot date: 2026-09-27. Host: Windows 11, Ryzen 7 2700X (8C/16T), MinGW g++ (scoop), raylib host window.
**Nothing is committed.** All work is uncommitted in the nested repo `tools/PS2Recomp` (see "Uncommitted state").

## 1. Where it is stuck right now

The game boots, shows the "No game data present on memory card" notice, then (with the fixes below) moves on
to play the intro FMV `\PSS\ST17_00N.PSS`. **The FMV phase runs at ~2.2 VBlanks/s (target 60).**

Cause, measured with the host profiler (`PS2_HOST_PROFILE_FILE`, see §5):

- Three guest threads at priority 41 rotate through `RotateThreadReadyQueue` (syscall 0x2B, wrapper `0x75D2D0`):
  - thread 5 = idle thread, `sub_00775D90`: `for(;;) RotateThreadReadyQueue(41)`.
  - thread 6 = decoder, `sub_00776B08`: yield, poll `func_776DE8` for stream data, `sceMpegGetPicture` (HLE stub).
  - thread 1 = stream feeder: `sceMpegDemuxPssRing` (HLE), `sceSdRemote`, etc.
- ~156k scheduler turns per host second at ~6 µs each. Each turn advances guest time by only ~67 EE cycles,
  because **syscalls and context switches cost zero guest cycles** in this runtime. Guest time therefore runs at
  ~3.5% of real speed, and the CD stream data the decoder waits for (delivered on guest-time deadlines) trickles in.

**The next step, implemented but never run** (the user interrupted the test): charge kernel time.
- `ps2xRuntime/src/lib/ps2_runtime.cpp`, `PS2Runtime::handleSyscall`: `accountCycles(200)` per syscall.
- `ps2xRuntime/src/lib/Kernel/EeScheduler.cpp`, `EeScheduler::makeRunning`: `accountCycles(800)` per thread switch.
- Built and linked as `output/diag_perf/NobleArchimedes_kcycles.exe`. **Untested.**
- Expected result: ~1,000 cycles per yield, so guest time runs at about 50% of real speed in the FMV loop.
- The constants are estimates, not measurements. They change guest timing globally; see §4 (risks).

After that, the remaining host cost per scheduler turn has three parts:
- `pendingEvents`: ~1.5 µs per call, twice per turn;
- the guest slice: ~3.7 µs;
- thread switches that still throw (see §2.3).

## 2. Fixes made in this session (all uncommitted)

### 2.1 Deadlock at the memory-card notice (the "stuck, background stops moving" bug) — FIXED, verified in game
- **Symptom:** the notice appears and the background animation freezes; 100% of guest PC samples are at `0x420740`.
- **The stuck loop:** `sub_00420710` does `do { WaitSema(m); empty = all 11 DMA-queue slots @0xAC3C40 are 0; SignalSema(m); } while(!empty)`.
  The queue is drained by the DMAC completion interrupt handler (GIF ch2 had CIS2 and CIM2 set, and slot 2 was still occupied).
- **Root cause:** `EeScheduler::checkpointDue` returned false whenever `guestDispatchDepth() != 0`
  ("Nested native calls must unwind first"). `sub_00420710` is called nested (from `0x443D30`), so the spin never
  reached a safe point. No interrupts, no VBlank (the vsync counter was frozen at 772), and no switch to
  ready thread 4 (priority 32, higher than thread 1's 41).
- **Fix:** nested checkpoints may now unwind. Generated code already unwinds by returning:
  `if (!dispatchGuestBranch(...)) return;`, and every function is resumable at its loop heads and return addresses.
  Two exceptions remain blocked:
  - (a) runtime code that called a guest function natively (SIF RPC callback/server in `Kernel/Syscalls/RPC.cpp`),
    tracked by `ps2_guest_dispatch::NativeGuestCallScope`;
  - (b) `ctx->pc == entry PC of the innermost callee` (the dispatcher reads that as "returned normally").
- **Files:** new `ps2xRuntime/include/runtime/ps2_guest_dispatch_state.h`, `ps2_runtime.cpp` (`DispatchDepthScope` records
  the callee entry PC; free functions `nativeGuestCallActive()` and `currentCalleeEntryPc()`), `RPC.cpp`, `EeScheduler.cpp`.
- **Known imperfection:** `DispatchDepthScope` sets `s_calleeEntryPc = targetPc` *before* the dispatch-level
  `checkpointDue` call in `dispatchGuestBranch`. So dispatch-level checkpoints in nested frames are always refused;
  only backward-edge checkpoints unwind. The fix: set the entry PC only around the actual `targetFn`/`nextFn` calls.
- **Not yet done:** run `ps2x_tests` (scheduler and interrupt tests) against this change.

### 2.2 Missing FMV files — FIXED
`sceCdSearchFile` looks under `extracted/`, and `extracted/PSS` did not exist, so the game retried forever.
I extracted `PSS/` (25 files, 2.2 GB) from `Castlevania - Curse of Darkness (USA).iso` with `tools/ps2_iso_reader.py`.
`DUMMY.BIN` from the ISO is still not extracted; it may never be needed.

### 2.3 Exception-free thread switch after syscalls — implemented and tested once (FMV: 0.6 → 2.2–3.4 VBlanks/s)
- **Before:** every thread switch threw `EeDispatcherTransfer` (~5–9 µs on MinGW SEH).
- **Now:** `EeScheduler::transferIfRequested(interruptSafe, ctx)` defers the switch instead of throwing when the
  syscall returns straight to its caller (the words at `ctx->pc` are `jr $ra` / `nop`) and no native guest call is active.
- **How the deferral works:**
  - it sets `m_deferredTransfer`;
  - `dispatchGuestBranch` returns false right after `targetFn`/`nextFn` while the flag is set;
  - `EeScheduler::run` clears the flag after each guest run.
- All callers in `Syscalls/Sync.cpp` and `Syscalls/Thread.cpp` now pass `ctx`.
- `blockCurrent` (WaitSema, SleepThread…) still throws; the same technique could apply there.

### 2.4 Yield-spin fast-forward — implemented, fires rarely (4 times in 200 s), harmless
- **What it does:** `EeScheduler::noteYield`. If every ready thread at the running priority has yielded with no kernel state
  change (`m_progressEpoch`, bumped in `publishSnapshot()` and on interrupt-handler dispatch) and at most 4,096 cycles
  between yields, it advances guest time to the next deadline.
- **Why it rarely fires:** thread 1 does real work between yields.
- **Log line:** `[spin-fast-forward]`.

### 2.5 Controller input path — investigated, not the blocker
- **`scePad*` reads work:** they are HLE stubs in `Kernel/Stubs/Pad.cpp`, fed by raylib gamepad/keyboard through `ps2_pad.cpp`.
- **Presses arrive:** the game reads the pad about 60 times/s, and scripted presses reached it (`pressedReads=109`).
- **Oddity, possibly relevant later:** the stub models a digital-only pad.
  - `scePadInfoMode(PAD_MODETABLE)` lists only ID 4, so the game (`0x4050F8` / `0x405040`) never switches to analog (ID 7).
  - `scePadEnterPressMode` is called every frame, and the status data stays `0x41`.
  - A real DualShock 2 reports the table `[4, 7]` and `0x73`/`0x79`.
  - Fix this if the game ignores input later.
- **Also:** `ps2_pad.cpp` ignores the keyboard whenever gamepad 0 exists.
- **New opt-in tools:** `PS2_PAD_TRACE=1` (per-second call counts, raylib gamepad detection, last status bytes) and
  `PS2_PAD_SCRIPT="20:cross,23:start"` (seconds after the first pad read, 250 ms presses).

### 2.6 Performance work earlier in this session (menu screen: 0.1 → 33–42 VBlanks/s)
All measured on the memory-card screen, which turned out to be the deadlocked state. Details are in
`output/perf-notes.md`.
- **Async stdio relay and gated logs:** `ps2_async_stdio.cpp`; the logs are behind `PS2X_ENABLE_AGRESSIVE_LOGS=OFF`.
- **Multithreaded GS rasterizer:** 8 row-band workers, per-page hazard tracking, and asynchronous present.
- **IOP fixes:** IOP batching, and the SPU2 STATX DMA-busy bit fix in `ps2xIOP` (with a test).
- **Allocator-spin fast-forward:** `isQueueSpin` in `checkpointDue`, a game-specific hack.
- **Sprite rasterizer fast path, bit-exact:** `gs_cpu_backend.cpp`, `DrawSpriteTexturedFast` / `DrawSpriteTexturedRows`
  / `WritePixelRow`, plus `GSMem::RowAccess` in `ps2_gs_memory.h`:
  - row-hoisted swizzle addressing;
  - per-draw CLUT decode;
  - SSE2 bilinear filtering;
  - direct texture reads when the draw cannot write its sampled pages (`TexturePageCache::MatchesMemory`/`Load`).
- **Debug-snapshot throttling:** `EeScheduler::publishSnapshot` is dirty-flag throttled to 10 ms, published immediately
  outside `run()` and before blocking. It was 12.7% of EE time plus heap churn. Built (`NobleArchimedes_snapfix.exe`)
  but never measured.

## 3. Validation assets
- **GS differential oracle (bit-exact, compares hashes of all 4 MiB of VRAM):** `output/diag_perf/run_raster_diff.sh <seed> <cases> <mode> [threads]`
  and `run_raster_matrix.sh <cases> <seeds...>`.
  - The reference rasterizer snapshot is in `output/diag_perf/reference_gs/`.
  - Modes: single, disjoint, sequence, pingpong, sprites, sprites-disjoint, feedback, and stale (synchronous only).
  - Last full matrix (seeds 81 and 82, 56 runs): all identical. Five transient diffs were traced to two matrix runs
    overwriting each other's files; the runner now uses PID-tagged files.
  - Mutation-tested: rounding, Z write, overlap guard, and stale-page check.
- **Replay benchmark:** `ps2xRuntime/tests/gs_sprite_raster_bench.cpp`, run on captured real draws in
  `output/diag_perf/draw_captures/` (`PS2_GS_CAPTURE_DIR` together with `PS2_GS_DRAW_STATS=1` produces them).
- **IOP tests:** pass. **`ps2x_tests`:** last known 432/437 (5 pre-existing failures), **not re-run** after the
  scheduler changes (§2.1, 2.3, 2.4, snapshot throttling). Run them first.

## 4. Risks and things to clean up
- **Build flags:** the CMake cache was changed to `CMAKE_CXX_FLAGS_RELEASE="-O3 -DNDEBUG -g"` for profiling. Revert with
  `cmake -S tools/PS2Recomp -B tools/PS2Recomp/build -DCMAKE_CXX_FLAGS_RELEASE="-O3 -DNDEBUG"`.
- **Guest chunk flags:** chunks are now built with `-O2 -fno-strict-aliasing -fwrapv` (`tools/build_recomp_chunks.py`
  `GUEST_OPT_FLAGS`); they were `-O0`. No visible regression, and no measurable speed change either.
- **Kernel cycle costs (§1):** these change guest timing globally. Verify that menus, audio and FMV pacing still behave.
- **Log gating that didn't apply:** `dispatchGuestBranch` prints `[checkpointDue] ...` on every true dispatch-level
  checkpoint. I tried to gate it behind `PS2_IF_AGRESSIVE_LOGS`, but the edit did not apply (string mismatch). Do it,
  since it can flood stderr.
- **Temporary instrumentation to remove or make opt-in:**
  - the EE guest-PC sampler in `checkpointDue` (`[pc-profile]`);
  - the IOP PC sampler and RAM dump in `ps2xIOP/src/emulator/iop_emulator.cpp` `step()`;
  - `HostProfile` periodic report;
  - `PS2_SPIN_DIAG` block in `checkpointDue`;
  - `DrawStats` (`PS2_GS_DRAW_STATS`);
  - pad trace.
- **`isQueueSpin`** (hard-coded PCs in `checkpointDue`) is a game-specific hack from earlier work. With §2.1 it may no
  longer be needed; test removing it.
- **Power plan:** Windows is on the "Power saver" plan (CPU held at ~2.2 GHz), which roughly halves every number here.
  Do not change it without asking the user.
- **Pre-existing modifications:** some files listed below were already modified before this session (for example
  `iop_cdvd.cpp`, `ps2_vfs.cpp`, `CD.cpp`, `GS.cpp`). Don't assume every diff is from this session.

## 5. How to build, run and measure
```
# runtime library (the nested CMake build)
cmake --build tools/PS2Recomp/build --config Release --target ps2_runtime --parallel 8
# guest chunks + host objects (only stale ones; ee_scheduler.h changes rebuild chunks 27, 31 and main, ~7 min;
# ps2_runtime.h changes rebuild ALL 33 chunks, ~70 min with 4 jobs, so avoid touching it)
python tools/build_recomp_chunks.py --jobs 4
# link a candidate (keep the root NobleArchimedes.exe untouched)
python tools/link_noble_archimedes.py output/diag_perf/NobleArchimedes_<name>.exe
# timed capture: in-memory stdout/stderr, host profile to <OutDir>\host_profile.log, screenshots
powershell output/diag_perf/run_capture_nul.ps1 -Exe <exe> -OutDir <dir> -Seconds 150 -SaveLogs
```
- Boot to the notice takes about 100 s of wall time at the current speed. Game windows appear on the user's desktop,
  so warn them before each run.
- **Profiling:**
  - `PS2_RIP_SAMPLES=<file>` (EE thread) and `PS2_RIP_SAMPLES_GS0=<file>` (GS worker 0), then
    `output/diag_perf/symbolize_samples.py <exe> <file>` or `abs_line_profile.py`. Link with `-g` (see
    `build_link_command` plus `-g`) for line-level results; the runtime uses LTO.
  - The `host_profile.log` line `vsync=+N (X/s)` is the frame-rate metric.

## 6. Suggested next steps, in order
1. Run `ps2x_tests`, and fix any regressions from the §2.1/§2.3/§2.4 scheduler changes.
2. Test `NobleArchimedes_kcycles.exe` in the FMV phase. If the FMV plays at about half speed or better, keep it and
   tune the constants; otherwise profile again.
3. Make `blockCurrent` deferrable like §2.3, and cut the per-turn cost of `processPendingEvents`.
4. Fix the `DispatchDepthScope` entry-PC ordering (§2.1 known imperfection).
5. Continue into the title screen and gameplay. Then revisit the frame rate there, where triangles and VU1 will
   dominate instead of sprites. Fix the pad analog/pressure modes if input is ignored.
