# Third-party source and licensing

No game assets, proprietary SDKs, dependency binaries or generated game implementations are included.

| Project | Reference | Treatment |
| --- | --- | --- |
| PS2Recomp | https://github.com/ran-j/PS2Recomp — `75d729ce40d7eed9649fd4bb05628dee520f3d0c` | Submodule plus runtime source patch. GPL-3.0 upstream terms continue to apply. Copy in `licenses/PS2Recomp-GPL-3.0.md`. |
| paraLLEl-GS / Granite | https://github.com/Arntzen-Software/parallel-gs | Acquired locally by pinned fetch script; small transfer patch included. Retain each upstream/dependency notice. |
| PCSX2 | https://github.com/PCSX2/pcsx2 — `646df006a4688063e56c0826e7ea4b8bb0c112c4` | Acquired locally. GPL-3.0-or-later; see upstream `COPYING.GPLv3` and third-party notices. GS consumer/glue is intended for this GPL-covered combination. |
| raylib, Dear ImGui, rlImGui, FFmpeg and other build dependencies | PS2Recomp build references | Fetched locally, not bundled. Their own license/notice terms apply. |
| Play! | https://github.com/jpd002/Play- | Optional VU loader interface only; optimized DLL and translated game microprograms excluded. |

Source references do not replace corresponding-source/license/notice obligations when distributing combined works or binaries. No new blanket license is assigned to all project-authored files, and upstream work is not relicensed. Public hosting does not mean public domain. No rights to Konami game content are granted.
