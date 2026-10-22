#!/usr/bin/env python3
"""Retarget the Fab Free Animation Library locomotion onto SK_Hector.

Source assets live under /Game/FreeAnimationLibrary (the pack's own root, which is
what its internal references expect -- copying it under an extra folder broke every
animation's skeleton link). Builds two IK Rigs, an IK Retargeter with auto-mapped
chains, then batch-retargets idle/walk/jog into /Game/Characters/Hector/Retargeted.
"""
import unreal

SOURCE_MESH = "/Game/FreeAnimationLibrary/Demo/Characters/Mannequins/Meshes/SK_Mannequin"
TARGET_MESH = "/Game/Characters/Hector/SK_Hector"
RIG_DIR = "/Game/Characters/Hector/Retarget"
OUT_DIR = "/Game/Characters/Hector/Retargeted"
ANIM_DIR = "/Game/FreeAnimationLibrary/Animations"

WANTED = (("Idle", "anim_Idle"),
          ("Walk", "anim_Walk_Fwd_Loop_L"),
          ("Walk", "anim_Walk_Fwd_Loop_R"),
          ("Jog", "anim_Jog_Fwd_Loop_L"),
          ("Jog", "anim_Jog_Fwd_Loop_R"))

OUT = r"C:\Users\Madi\AppData\Local\Temp\retarget_out2.txt"
lines = []


def say(msg):
    lines.append(str(msg))


def flush():
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def get_asset(path):
    return unreal.EditorAssetLibrary.load_asset(path) if \
        unreal.EditorAssetLibrary.does_asset_exist(path) else None


def make(folder, name, cls, factory):
    path = "%s/%s" % (folder, name)
    existing = get_asset(path)
    if existing:
        say("  reuse %s" % path)
        return existing
    asset = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        name, folder, cls, factory)
    say("  %s %s" % ("created" if asset else "FAILED", path))
    return asset


def enum_variant(enum_name, *candidates):
    enum = getattr(unreal, enum_name, None)
    if enum is None:
        return None
    for c in candidates:
        v = getattr(enum, c, None)
        if v is not None:
            return v
    return None


try:
    src_mesh = get_asset(SOURCE_MESH)
    dst_mesh = get_asset(TARGET_MESH)
    say("source mesh: %s" % (src_mesh.get_name() if src_mesh else "MISSING"))
    say("target mesh: %s" % (dst_mesh.get_name() if dst_mesh else "MISSING"))
    if not (src_mesh and dst_mesh):
        raise RuntimeError("both meshes are required")

    for d in (RIG_DIR, OUT_DIR):
        if not unreal.EditorAssetLibrary.does_directory_exist(d):
            unreal.EditorAssetLibrary.make_directory(d)

    rigs = {}
    for label, mesh in (("mannequin", src_mesh), ("hector", dst_mesh)):
        rig = make(RIG_DIR, "IKRig_%s" % label, unreal.IKRigDefinition,
                   unreal.IKRigDefinitionFactory())
        if not rig:
            continue
        ctrl = unreal.IKRigController.get_controller(rig)
        try:
            ctrl.set_preview_mesh(mesh)
            say("  %s preview mesh set" % label)
        except Exception as exc:
            say("  %s set_preview_mesh failed: %s" % (label, exc))
        try:
            ok = ctrl.apply_auto_generated_retarget_definition()
            chains = ctrl.get_retarget_chains()
            say("  %s auto-chains ok=%s count=%d" % (label, ok, len(chains)))
        except Exception as exc:
            say("  %s auto-chain failed: %s" % (label, exc))
        rigs[label] = rig



    rt = make(RIG_DIR, "RTG_Hector", unreal.IKRetargeter, unreal.IKRetargetFactory())
    if rt and "mannequin" in rigs and "hector" in rigs:
        ctrl = unreal.IKRetargeterController.get_controller(rt)
        for rig, is_source, label in ((rigs["mannequin"], True, "source"),
                                      (rigs["hector"], False, "target")):
            try:
                ctrl.set_ik_rig(rig, is_source)
                say("  %s rig assigned" % label)
            except Exception as exc:
                say("  %s rig assign failed: %s" % (label, exc))
        try:
            ctrl.set_preview_mesh(dst_mesh)
        except Exception as exc:
            say("  preview mesh failed: %s" % exc)

        map_type = enum_variant("AutoMapChainType", "EXACT", "FUZZY", "CLEAR")
        say("  auto_map enum resolved to %s" % map_type)
        for attempt in (lambda: ctrl.auto_map_chains(map_type),
                        lambda: ctrl.auto_map_chains()):
            try:
                say("  auto_map_chains -> %s" % attempt())
                break
            except Exception as exc:
                say("  auto_map_chains attempt failed: %s" % exc)
        try:
            ctrl.run_op_initial_setup()
            say("  op initial setup done")
        except Exception as exc:
            say("  op initial setup failed: %s" % exc)

        assets = []
        for folder, name in WANTED:
            a = get_asset("%s/%s/%s" % (ANIM_DIR, folder, name))
            if a:
                assets.append(a)
                say("  queued %s" % name)
            else:
                say("  NOT FOUND %s/%s" % (folder, name))

        if assets:
            inputs = unreal.IKRetargetBatchOperationInputs()
            for field, value in (("assets_to_retarget", assets),
                                 ("source_mesh", src_mesh),
                                 ("target_mesh", dst_mesh),
                                 ("ik_retarget_asset", rt),
                                 ("target_path", OUT_DIR),
                                 ("prefix", "RTG_"),
                                 ("include_referenced_assets", False),
                                 ("overwrite_existing_files", True)):
                try:
                    inputs.set_editor_property(field, value)
                except Exception as exc:
                    say("  inputs.%s not settable: %s" % (field, exc))
            try:
                created = unreal.IKRetargetBatchOperation.run_batch_retarget(inputs)
                say("  batch produced %d assets" % (len(created) if created else 0))
                for a in (created or []):
                    say("    %s" % a.package_name)
            except Exception as exc:
                say("  BATCH FAILED: %s" % exc)
except Exception as exc:
    say("RETARGET FAILED: %s" % exc)

flush()
unreal.log("[NA-RETARGET] wrote %d lines" % len(lines))
