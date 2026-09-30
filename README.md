# Noble Archimedes

Work-in-progress native Windows recompilation host for Castlevania: Curse of Darkness (USA, SLUS-21168).

## Preserved progress

- Native host, camera, input, overlay, and ISO virtual filesystem integration.
- Recompilation analysis, generation, incremental build, and linking helpers.
- PS2 runtime and IOP changes covering scheduling, interrupts, asynchronous I/O, CD/MPEG, memory cards, controllers, GS rendering, and VIF handling.
- Regression tests and investigation notes in `output/`. These dated notes describe experiments and known limitations; they are not a claim that gameplay is complete.

## Restore the runtime changes

The upstream PS2Recomp source is referenced as a submodule rather than vendored. Its local changes and new runtime tests are preserved in `patches/ps2recomp-progress.patch`.

```sh
git submodule update --init --recursive
git -C tools/PS2Recomp apply --unidiff-zero ../../patches/ps2recomp-progress.patch
```

Upstream base: `75d729ce40d7eed9649fd4bb05628dee520f3d0c` at https://github.com/ran-j/PS2Recomp . Upstream is GPL-3.0 licensed; its terms continue to apply to modifications. No new blanket license is assigned by this snapshot.

See [BUILDING.md](BUILDING.md) for the existing Windows build workflow. A fresh checkout also needs the upstream dependencies/toolchain configured and guest sources generated locally from your own legally obtained game copy. The build documentation reflects the development machine's configured build tree.

## Game material excluded

This repository contains no game ISO, extracted game files, translated/recompiled game implementation, game artwork, screenshots, audio, movies, memory dumps, saved games, compiled game executable, or bundled dependency binaries. Game-derived sources must be regenerated locally and stay ignored. No proprietary SDK or third-party asset bundle is included. Runtime modifications are distributed as source patches with the upstream dependency referenced separately.

Verified snapshot checks: 8 build-helper tests and 2 optimizer tests passed. Full game/runtime validation remains described in the investigation notes.
