# PCSX2 GS-only consumer

This experimental consumer builds the unmodified GS sources from PCSX2 commit
`646df006a4688063e56c0826e7ea4b8bb0c112c4`. It exposes a C ABI and opens a
surfaceless D3D11 GS renderer. It does not initialize or execute upstream EE,
IOP, VU, VM, input, memory-card, or audio emulation. `host_glue.cpp` supplies
window/UI/statistics/configuration metadata. Calls to unavailable non-GS
services fail closed; software rendering is not an exposed renderer.

From the repository root:

```
python tools/pcsx2_gs/build.py toolchain
python tools/pcsx2_gs/bootstrap.py
python tools/pcsx2_gs/build.py consumer
python tools/pcsx2_gs/test_real_module.py
```

The private artifact-freezing scripts and their machine-specific evidence are not
published. These build/test commands have not been rerun from a clean public
checkout; see the root BUILDING.md for current limitations.

The compiler, STL and CRT use existing MSVC 14.40.33807 with Windows SDK
10.0.22621.0 via a private child-process environment. Bootstrap downloads the
official PCSX2 Windows dependency asset, checks the release SHA256 and extracts
it privately. No installation, elevation or upstream source mutation occurs.
The complete dependency archive is retained; `runtime_bundle` contains only
the built module and its package-provided transitive DLL imports. The OS and
installed MSVC redistributable supply the remaining imports. The `resources_utf8`
configuration points to the pinned upstream `bin/resources` directory.

ABI1 uses caller-owned buffers and opaque lifetime tokens, with one process-wide
GS instance. Each API call is serialized. Callers provide clean, masked x87 and
MXCSR state and restore their complete native state outside the module; Win64
calling conventions alone are insufficient. No C++ allocation or exception
crosses the ABI. `flush` submits pending GS work and waits on a D3D11 EVENT
completion query. RGBA NULL-query and copy calls reuse one owned snapshot for
the same epoch and dimensions.

Physical GIF paths are numbered 1/2/3. PATH1 uses the actual upstream
`GSState::Transfer<0>`. Its upstream incomplete-loop reset and EOP early-return
require complete EOP packets, so the consumer collects fragments until EOP.
Cross-path input, flush, FIFO, register/image writes and state observers reject
while PATH1 is incomplete. An identical privileged snapshot is a NOP; changes
reject before mutation. Reset and close deliberately discard incomplete input.
Standalone A+D and image submissions use upstream parser index3; partial image
bytes reject intervening retargeting. These restrictions must be checked against
an actual native game GIF capture before hybrid gameplay is accepted.

Real module tests exercise D3D11 open/reset/close; fragmented image transfers on
all three physical paths; independent synthetic parser; FIFO; sprite GPU VRAM
readback; privileged PCRTC/vsync and RGBA RGB pixels; pending-input rejection;
stale handles and reopen; and a 4MB VRAM snapshot. They do not establish full
game correctness or performance. Parent-owned runtime tests qualify the complete
FP call boundary and native/hybrid integration separately.

PCSX2 GS is GPL-3.0-or-later; see the pinned `COPYING.GPLv3`. A distributed linked
consumer must satisfy its source/license obligations and dependency notices.
No stock PCSX2 executable or old GSdx plugin exports are used.
