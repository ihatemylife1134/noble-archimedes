# Building Noble Archimedes

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

Run the build-helper regression suite with:

```powershell
python -m unittest discover -s tests -p test_build_helpers.py
```
