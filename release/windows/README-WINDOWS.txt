NOBLE ARCHIMEDES - ALPHA 0.2.0 WINDOWS KIT
==========================================

This public kit contains source, launchers and documentation. It deliberately
does not contain NobleArchimedes.exe, game code, an ISO, an extracted ELF, the
private optimized VU module, PCSX2 binaries, or dependency DLLs. Build those
parts locally by following BUILDING.md and docs/BUILD_VARIANTS.md.

GAME SELECTION
--------------
Only the USA SLUS-21168 release is supported. Place your legally obtained image
beside the locally built executable with this exact filename:

  Castlevania - Curse of Darkness (USA).iso

Extract SLUS_211.68 into the adjacent extracted directory using the command in
BUILDING.md. The resulting path must be:

  extracted\SLUS_211.68

GPU RENDERER SELECTION
----------------------
Double-click "Launch Native.cmd" for the Vulkan paraLLEl-GS path.

Double-click "Launch PCSX2 GS.cmd" for the experimental GS-only bridge. That
path also needs noble_pcsx2_gs.dll, its dependency bundle and a host built with
PS2X_ENABLE_PCSX2_GS=ON. It does not start the complete PCSX2 emulator.

Inside a running build, press F1, open Graphics, choose Native or Hybrid
(PCSX2 GS), exit, and restart. The saved setting applies on the next launch.

STATUS
------
This is a development alpha. Sustained 58-60 gameplay updates/s has not been
achieved. See CHANGELOG.md and docs\PROJECT_STATUS.md for measured results,
known limitations and the remaining native engine-seam work.
