#!/usr/bin/env python3
"""Retarget the mocap locomotion onto SK_HectorBase (the new player character)."""
import unreal

RIG_DIR = "/Game/Characters/HectorBase/Retarget"
OUT_DIR = "/Game/Characters/HectorBase/Retargeted"
SRC_RIG = "/Game/Characters/Hector/Retarget/IKRig_mannequin"
DST_RIG = "/Game/Characters/HectorBase/Retarget/IKRig_HectorBase"
SRC_MESH = "/Game/Free_Spells/Demo/Characters/Mannequins/Meshes/SKM_Manny"
DST_MESH = "/Game/Characters/HectorBase/SK_HectorBase"
ANIM_DIR = "/Game/FreeAnimationLibrary/Animations"
WANTED = (("Idle", "anim_Idle"),
          ("Walk", "anim_Walk_Fwd_Loop_L"),
          ("Walk", "anim_Walk_Fwd_Loop_R"),
          ("Jog", "anim_Jog_Loop_Fwd"),
          ("Jog", "anim_Jog_Loop_Bwd"))
OUT = r"C:\Users\Madi\AppData\Local\Temp\retarget_base.txt"
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
    say("rigs: src=%s dst=%s meshes: src=%s dst=%s"
        % (bool(src_rig), bool(dst_rig), bool(src_mesh), bool(dst_mesh)))
    if not (src_rig and dst_rig and src_mesh and dst_mesh):
        raise RuntimeError("missing inputs")

    if not unreal.EditorAssetLibrary.does_directory_exist(OUT_DIR):
        unreal.EditorAssetLibrary.make_directory(OUT_DIR)

    # Chains must be rebuilt now that the skeleton asset actually exists on disk;
    # the rig saved earlier referenced bones that were not persisted.
    for rig, mesh in ((src_rig, src_mesh), (dst_rig, dst_mesh)):
        rig.set_editor_property("preview_skeletal_mesh", mesh)
        rc = unreal.IKRigController.get_controller(rig)
        ok = rc.apply_auto_generated_retarget_definition()
        say("rig %-22s chains=%d ok=%s" % (rig.get_name(),
                                            len(rc.get_retarget_chains()), ok))
        unreal.EditorAssetLibrary.save_asset(pkg(rig), only_if_is_dirty=False)

    rt = get_asset("%s/RTG_HectorBase" % RIG_DIR)
    if not rt:
        rt = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            "RTG_HectorBase", RIG_DIR, unreal.IKRetargeter,
            unreal.IKRetargetFactory())
    ctrl = unreal.IKRetargeterController.get_controller(rt)
    ctrl.set_ik_rig(unreal.RetargetSourceOrTarget.SOURCE, src_rig)
    ctrl.set_ik_rig(unreal.RetargetSourceOrTarget.TARGET, dst_rig)
    ctrl.auto_map_chains(unreal.AutoMapChainType.EXACT, True)
    unreal.EditorAssetLibrary.save_asset(pkg(rt), only_if_is_dirty=False)
    say("retargeter configured")

    assets = []
    for folder, name in WANTED:
        a = get_asset("%s/%s/%s" % (ANIM_DIR, folder, name))
        if a:
            assets.append(a)
    say("animations: %d" % len(assets))

    if assets:
        created = unreal.IKRetargetBatchOperation.duplicate_and_retarget(
            [unreal.EditorAssetLibrary.find_asset_data(pkg(a)) for a in assets],
            src_mesh, dst_mesh, rt, target_path=OUT_DIR, prefix="RTG_",
            overwrite_existing_files=True)
        say("retargeted %d" % (len(created) if created else 0))
        for a in (created or []):
            say("  %s" % a.package_name)
except Exception as exc:
    say("FAILED: %s" % exc)

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
unreal.log("[NA-RETARGETBASE] wrote %d lines" % len(lines))
