"""Probe the source clips and whether AnimSequence -> FBX export is scriptable.

The ActionRPG clips are .uasset bound to SK_Mannequin_Skeleton, so unlike the
ActorCore FBXs they cannot simply be imported onto the character's skeleton. Two
routes exist: export them to FBX and re-import (the path that now works), or fix
the IK retargeter (which still emits bind poses). This establishes whether the
first is available.

Also inspects the candidate clips for the Phase 1 slice so the sources are chosen
from real data rather than filenames.
"""
import os

import unreal

OUT = r"C:\Users\Madi\AppData\Local\Temp\sword_probe.txt"
ANIM_DIR = "/Game/Characters/Animations"
CANDIDATES = [
    "Anim_Sword_Idle",
    "AM_Attack_Sword",
    "Combat_Blade_Swing_Far",
    "Anim_Sword_Whirlwind",
    "Attack",
    "Attack03",
    "Sword_Walk_Foward",
    "Sword_Run_Forward",
]
lines = []


def say(m):
    lines.append(str(m))


def load(path):
    return unreal.EditorAssetLibrary.load_asset(path) if \
        unreal.EditorAssetLibrary.does_asset_exist(path) else None


try:
    say("=== export APIs ===")
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    say("AssetTools export members: %s" % [
        m for m in dir(tools) if "export" in m.lower()])
    say("AssetExportTask members: %s" % [
        m for m in dir(unreal.AssetExportTask) if not m.startswith("_")][:25])

    say("")
    say("=== candidate clips ===")
    for name in CANDIDATES:
        path = "%s/%s" % (ANIM_DIR, name)
        asset = load(path)
        if not asset:
            say("%-26s MISSING" % name)
            continue
        cls = asset.get_class().get_name()
        skeleton = "?"
        try:
            skeleton = asset.get_editor_property("skeleton").get_name()
        except Exception:  # noqa: BLE001
            pass
        extra = ""
        if isinstance(asset, unreal.AnimSequence):
            extra = "frames=%s len=%.2f" % (
                unreal.AnimationLibrary.get_num_frames(asset),
                asset.get_editor_property("sequence_length"))
        elif isinstance(asset, unreal.AnimMontage):
            try:
                tracks = asset.get_editor_property("slot_anim_tracks")
                names = []
                for t in tracks:
                    for seg in t.get_editor_property("anim_track").get_editor_property("segments"):
                        seq = seg.get_editor_property("anim_reference")
                        if seq:
                            names.append(seq.get_name())
                extra = "slots=%d sequences=%s" % (len(tracks), names)
            except Exception as exc:  # noqa: BLE001
                extra = "montage inspect failed: %s" % exc
        say("%-26s %-14s skel=%-24s %s" % (name, cls, skeleton, extra))

    say("")
    say("=== export attempt ===")
    src = load("%s/Anim_Sword_Idle" % ANIM_DIR)
    if not src:
        say("no source to export")
    else:
        out_dir = r"C:\Projects\NobleArchimedes\ArtSource\ActionRPG\Exported"
        os.makedirs(out_dir, exist_ok=True)
        say("members on the sequence mentioning export: %s" % [
            m for m in dir(src) if "export" in m.lower()])
        try:
            task = unreal.AssetExportTask()
            task.set_editor_property("object", src)
            task.set_editor_property("filename", os.path.join(out_dir, "Anim_Sword_Idle.fbx"))
            task.set_editor_property("automated", True)
            task.set_editor_property("prompt", False)
            task.set_editor_property("replace_identical", True)
            ok = tools.run_asset_export_task(task)
            say("run_asset_export_task = %s" % ok)
        except Exception as exc:  # noqa: BLE001
            say("run_asset_export_task failed: %s" % exc)
        exported = os.path.join(out_dir, "Anim_Sword_Idle.fbx")
        if os.path.exists(exported):
            say("exported %.2f MB" % (os.path.getsize(exported) / 1048576.0))
        else:
            say("no FBX produced")
except Exception as exc:
    say("FAILED: %s" % exc)

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
unreal.log("[NA-SWORDPROBE] wrote %d lines" % len(lines))
