#!/usr/bin/env python3
"""Retarget the old procedural Hector clips onto the new player character.

The stub rig (IKRig_hector, 9 chains) and the new character (IKRig_HectorBase,
29 chains) share 13 bone names, so auto-map plus the batch operation carries the
attack/guard/jump/death clips across. Without this, swapping the mesh would break
combat because montages are bound to the old skeleton.
"""
import unreal

SRC_RIG = "/Game/Characters/Hector/Retarget/IKRig_hector"
DST_RIG = "/Game/Characters/HectorBase/Retarget/IKRig_HectorBase"
SRC_MESH = "/Game/Characters/Hector/SK_Hector"
DST_MESH = "/Game/Characters/HectorBase/SK_HectorBase"
SEARCH_DIR = "/Game/Characters/Hector"
OUT_DIR = "/Game/Characters/HectorBase/Retargeted"
OUT = r"C:\Users\Madi\AppData\Local\Temp\retarget_attacks.txt"
lines = []


def say(m):
    lines.append(str(m))


def get_asset(p):
    return unreal.EditorAssetLibrary.load_asset(p) if \
        unreal.EditorAssetLibrary.does_asset_exist(p) else None


def pkg(a):
    return a.get_path_name().split(".")[0]


try:
    src_rig = get_asset(SRC_RIG)
    dst_rig = get_asset(DST_RIG)
    src_mesh = get_asset(SRC_MESH)
    dst_mesh = get_asset(DST_MESH)
    say("rigs src=%s dst=%s meshes src=%s dst=%s"
        % (bool(src_rig), bool(dst_rig), bool(src_mesh), bool(dst_mesh)))
    if not all((src_rig, dst_rig, src_mesh, dst_mesh)):
        raise RuntimeError("missing inputs")

    rt = get_asset("/Game/Characters/HectorBase/Retarget/RTG_StubToBase")
    if not rt:
        rt = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            "RTG_StubToBase", "/Game/Characters/HectorBase/Retarget",
            unreal.IKRetargeter, unreal.IKRetargetFactory())
    ctrl = unreal.IKRetargeterController.get_controller(rt)
    ctrl.set_ik_rig(unreal.RetargetSourceOrTarget.SOURCE, src_rig)
    ctrl.set_ik_rig(unreal.RetargetSourceOrTarget.TARGET, dst_rig)
    ctrl.auto_map_chains(unreal.AutoMapChainType.EXACT, True)
    say("retargeter stub->base mapped")
    unreal.EditorAssetLibrary.save_asset(pkg(rt), only_if_is_dirty=False)

    clips = []
    for path in unreal.EditorAssetLibrary.list_assets(SEARCH_DIR, recursive=True):
        name = path.split("/")[-1].split(".")[0]
        if name.startswith("AN_Hector_"):
            a = unreal.EditorAssetLibrary.load_asset(path)
            if isinstance(a, unreal.AnimSequence):
                clips.append(a)
    say("found %d source clips" % len(clips))

    if clips:
        created = unreal.IKRetargetBatchOperation.duplicate_and_retarget(
            [unreal.EditorAssetLibrary.find_asset_data(pkg(a)) for a in clips],
            src_mesh, dst_mesh, rt, target_path=OUT_DIR, prefix="RTG_",
            overwrite_existing_files=True)
        say("retargeted %d" % (len(created) if created else 0))
        for a in (created or []):
            say("  %s" % a.package_name)
        # Batch-created assets exist only in memory. Without an explicit save the
        # folder never appears on disk and the next session sees nothing, even
        # though the operation reported success.
        saved = unreal.EditorAssetLibrary.save_directory(
            OUT_DIR, only_if_is_dirty=False, recursive=True)
        say("save_directory(%s) = %s" % (OUT_DIR, saved))
        on_disk = unreal.EditorAssetLibrary.does_directory_exist(OUT_DIR)
        say("directory exists after save = %s" % on_disk)
except Exception as exc:
    say("FAILED: %s" % exc)

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
unreal.log("[NA-RETARGETATTACKS] wrote %d lines" % len(lines))
