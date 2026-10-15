# Historical development build notes

The native executable is built with the repository scripts and the configured
CMake cache under `tools/PS2Recomp/build`. The verified Windows toolchain is
MinGW-w64 GCC/G++ 15.2, Python 3.12, and CMake/Ninja. The configured build tree
already contains the runtime and third-party dependencies; the game ISO must
remain in the repository root for a normal launch.

From the repository root in PowerShell, rebuild the runtime and IOP libraries,
then compile generated guest chunks and native host objects, and link the
executable:

```powershell
cmake --build tools/PS2Recomp/build --config Release --target ps2_runtime ps2_iop --parallel 2
python tools/build_recomp_chunks.py --jobs 2
python tools/link_noble_archimedes.py
```

The linker writes `NobleArchimedes.exe` in the repository root. To keep the
existing executable untouched while checking a candidate, pass an output path:

```powershell
python tools/link_noble_archimedes.py output/candidate/NobleArchimedes.exe
```

The link helper checks that all 32 numbered guest chunks and the entries chunk
are present, and that every object has a current GCC dependency file before it
links. The build script refreshes generated unity chunks, rebuilds stale guest
and host objects, and writes those dependency files. A complete guest chunk
rebuild took about 20 minutes on the verified host; use `--jobs 2` on memory-
constrained Windows hosts.

Both guest chunks and native host callbacks are compiled with `-O2`,
`-fno-strict-aliasing`, and `-fwrapv`. The `.o.flags` files record those options,
so changing optimization flags rebuilds the affected objects.

Run the build-helper regression suite with:

```powershell
python -m unittest discover -s tests -p test_build_helpers.py
```

The sound-bank regression compiles the local generated guest routines and
checks the startup command, per-channel status, rejected queue writes, and the
level bank loader's request/finish/data submission sequence. It also checks
the resource callback at `0x454B40` and the stack/register restoration at
the previously missing level setup return entry `0x500004`:

```powershell
python tools/test_sound_bank_status.py
```

Resource callback aliases are emitted by `tools/generate_resource_entries.py`
from the locally generated guest code. Unity generation refreshes this header
automatically; after updating aliases alone, regenerate it and rebuild
`runtime_stub_registry.cpp` before linking.

The two missed guest entry helpers in `src/recomp/guest_entry_compat.hpp` are
also generated locally by `tools/generate_guest_entries.py` from the ignored
guest instruction records. Unity generation refreshes them before compiling.
The translated header stays ignored; only its generator is published.

To reproduce New Game on Windows without showing a game window, start a bounded
headless probe, then run its menu driver in another terminal after `pid.txt`
appears:

```powershell
python tools/probe_headless.py output/candidate/NobleArchimedes.exe output/new_game_probe --seconds 600
python tools/probe_new_game.py output/new_game_probe
```

The probe copies the candidate beside the local assets, sends input only to
that process's hidden window, and removes its temporary executable on exit.
The driver enters a name and chooses to start without saving. Logs, captured
frames, and observed guest menu states remain in the specified output folder.
It reads guest RAM to navigate; it does not write guest RAM or send global
keyboard input. `tools/probe_guest_ram.py` also supports explicit read-only
inspection of a running probe by PID. Keep RAM dumps and game frames local.

Normal play avoids automatic PNG screenshots. Set `NOBLE_FRAME_CAPTURE=1`
to restore the periodic window screenshots; the headless probe's guest-frame
captures remain controlled separately by `PS2_FRAME_DUMP_PREFIX`.

GS register/draw history is paused by default during normal play. Set
`PS2_GS_HISTORY=1` to collect it from startup, or resume history in the GS debug
panel. Set `PS2_GUEST_PC_PROFILE=1` for the sampled guest-PC histogram. These
diagnostics add work to hot paths and should stay off for FPS measurements.
Detailed guest phase tracing requires `PS2_GUEST_FLOW_TRACE=1`; the tiny IOP-call
timing diagnostic requires `PS2_IOP_PROFILE=1`. Both are off during normal play.
Periodic window-side thread/GS diagnostics require `PS2_KERNEL_DIAGNOSTICS=1`;
memory-card operation logs require `PS2_MC_TRACE=1`.
Detailed host timers and counters are also off by default. Set
`PS2_HOST_PROFILE=1` for the full report, or `PS2_HOST_PROFILE=rate` for a
lightweight guest VBlank rate report without timing every scheduler operation.

For serial ordinary-input menu and name-entry measurements, use
`python tools/probe_menu_scenarios.py output/candidate/NobleArchimedes.exe output/menu_measurement --seconds 80 --observe-render-gate`.
The optional `--power-plan UUID` comparison restores the original Windows plan
in `finally`; omit it to measure the user's current settings. Each run saves
the executable hash, navigation states, VBlank rates, and original completion
gate/swap counters. These probes read guest RAM and send input only to their
own hidden game window. Add `--cursor-test` to exercise Up/Down movement in
the name-entry menu; the main-menu probe already exercises cursor movement.

VBlank rate and guest updates are separate measurements. The effective swap
interval depends on both the stored interval and the game's override flags;
MPEG contains 29.97 unique pictures/s. Measure both the VBlank counter and main
updates when checking full-speed 59–60 Hz execution. The render
gate at 9395B8 is cleared by the guest's queued completion callback. Its read-only
polling loop can fold complete 32-cycle polls, bounded by the next scheduler
event, EE timer, thread timeslice, and IOP batch; it never forces the gate clear.
The normal menu setting `A3DD30=0x01020100` has interval 1 and mode 2,
which permits one update per VBlank. `PS2_EE_RENDER_WAIT_DIAGNOSTICS=1`
reports why host pacing is rejected, including timer state and event deadlines;
leave it off for performance measurements. Sampled `PS2_MPEG_TRACE=1`
picture logs include monotonic milliseconds, delivered picture count, and
VBlank count for measuring actual playback speed.
Providing `PS2_HOST_PROFILE_FILE` alone retains the full diagnostic mode for
existing scripts. Headless probes select `rate` by default; add
`--env PS2_HOST_PROFILE=1` when investigating a time breakdown.

The optional Vulkan GS backend uses a pinned paraLLEl-GS checkout and retained
license notices under `ps2xRuntime/third_party`. Fetch and enable it before
building the runtime:

```powershell
python tools/PS2Recomp/ps2xRuntime/scripts/fetch_parallel_gs.py
cmake -S tools/PS2Recomp -B tools/PS2Recomp/build -DPS2X_ENABLE_PGS=ON
cmake --build tools/PS2Recomp/build --target ps2_runtime --parallel 4
python tools/link_noble_archimedes.py output/candidate/NobleArchimedes.exe
```

With that option enabled, the runtime tries Vulkan at startup and falls back to
the CPU renderer if initialization fails. Set `PS2_GS_BACKEND=cpu` to select the
CPU renderer explicitly. The GPU performs rasterization and uses GPU display
conversion for supported progressive logical displays (CT32/24/16/16S up to
640x448, a single source or identical display circuits). Unsupported layouts use
the compatibility presenter, preserving display dimensions and movie-source rules.
`PS2_GS_PGS_SCANOUT=compat` forces compatibility presentation for comparison;
`PS2_GS_PGS_SCANOUT=native` enables the upstream analog scanout for timing experiments.
Neither renderer changes guest cycle accounting or the native movie frame rate.

Headless probes write `rdram_base.txt` as an allocation hint. The read-only RAM
tool validates the game anchor and phase tables inside the supplied PID before
using this hint, avoiding a scan through unrelated Vulkan allocations:

```powershell
python tools/probe_guest_ram.py --base-file output/new_game_probe/rdram_base.txt 12345 0xAC23A4
```

Use `PS2_GS_BACKEND=cpu` when running the CPU raster/VRAM unit suites. Dedicated
GPU tests live under `ps2xRuntime/tests/pgs` and require a Vulkan device.

`PS2_GS_PGS_PROFILE=1` separates raw GIF processing, backend mutex wait, readback,
display conversion, clear, and Finish costs. Use a separate diagnostic run when
collecting these timings. To capture resumable VU workloads for offline replay,
create the output parent first, then use `PS2_VU_CAPTURE_PREFIX`,
`PS2_VU_CAPTURE_CHAIN=1`, `PS2_VU_CAPTURE_RESUME_ENTRY=14a0`,
`PS2_VU_CAPTURE_CHAIN_CALLS=1024`, and `PS2_VU_CAPTURE_COUNT=2`.
These bounded captures include a fresh execute followed by its ordered resumes;
the replay checks registers, data, cycle deltas, and emitted PATH1 packets.
Set `PS2_VU_CAPTURE_GATE_FILE` to a fresh, initially absent marker path to delay
capture until a chosen observed state. The driver can create that marker with
`--capture-gate-file` and `--capture-gate-state 4 7 3 1` for name entry. Select
`PS2_VU_CAPTURE_RESUME_ENTRY=140` for its hot draw chains; the older `14a0`
captures came from loading, not name entry. `--name-only` holds on that screen;
`--menu-only` exercises the title cursor and prevents the attract sequence.
Use the default short main-menu dwell when starting a new game, since a long
dwell can enter the attract movie before Cross is delivered.

MPEG decoding keeps at most four decoded RGBA pictures ahead. Incoming compressed
packets retain their original order, timestamps, and guest demux callbacks in an
owned queue; no frames are dropped. EOF waits for queued input and delayed frames
to drain. This bounds decoded-picture memory without changing native movie timing.

The RAM reader reports an invalid phase index from a validated allocation hint
without using it as an array offset. It can continue reading explicit guest words
for diagnostics; it does not modify the phase stack or enlarge its sixteen entries.

The render-completion observer has a synthetic regression covering normal
returns, pre-call yields, unwinding, deferred transfers and merged callbacks.
After building the runtime, run it with diagnostics off and on:

```powershell
python tools/PS2Recomp/ps2xRuntime/tests/run_ee_render_completion_observer_test.py
```

It compiles only the fixture and compares guest-state fingerprints and cycle
counts. It requires no game source or assets and leaves runtime archives intact.
