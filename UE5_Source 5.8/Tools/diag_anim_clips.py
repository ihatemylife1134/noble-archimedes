#!/usr/bin/env python3
"""Report whether the Hector animation clips actually contain bone data.

An AnimSequence with no bone tracks still looks valid by name and still plays:
it just outputs the reference pose, which is indistinguishable from a broken
state machine.
"""
import unreal

OUT = r"C:\Users\Madi\AppData\Local\Temp\diag_clips.txt"
FOLDER = "/Game/Characters/Hector"
lines = []

assets = unreal.EditorAssetLibrary.list_assets(FOLDER, recursive=True, include_folder=False)
for path in assets:
    asset = unreal.EditorAssetLibrary.load_asset(path)
    if not isinstance(asset, unreal.AnimSequence):
        continue
    keys = None
    for prop in ("number_of_sampled_keys", "NumberOfSampledKeys"):
        try:
            keys = asset.get_editor_property(prop)
            break
        except Exception:
            continue
    length = asset.get_play_length()
    frames = asset.get_number_of_frames() if hasattr(asset, "get_number_of_frames") else None
    lines.append("%-26s length=%.3fs frames=%s sampled_keys=%s"
                 % (asset.get_name(), length, frames, keys))

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
unreal.log("[NA-CLIPS] wrote %d sequences" % len(lines))
