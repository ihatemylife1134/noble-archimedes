#!/usr/bin/env python3
"""Probe exact property names for FBX import + anim asset creation in UE 5.8."""
import unreal


def say(msg):
    unreal.log_warning("[PROBE2] " + str(msg))


def props_of(obj):
    out = []
    try:
        for name in dir(obj):
            if name.startswith("_") or name in ("get_editor_property", "set_editor_property",
                                               "set_editor_property_by_name"):
                continue
            out.append(name)
    except Exception as exc:
        say("dir err " + str(exc))
    return sorted(set(out))


for cls_name in ("FbxImportUI", "FbxSkeletalMeshImportData", "FbxAnimSequenceImportData",
                 "AnimBlueprintFactory", "AnimMontageFactory", "AnimSequenceFactory",
                 "AnimBlueprint", "AnimMontage", "Skeleton", "AnimationAsset"):
    cls = getattr(unreal, cls_name, None)
    if cls is None:
        say("MISSING " + cls_name)
        continue
    say("=== %s ===" % cls_name)
    say("  " + ", ".join(props_of(cls)))

say("=== import_mesh (AssetImportTask) ===")
say("  " + ", ".join(props_of(unreal.AssetImportTask())))

say("=== anim bp factory instance ===")
try:
    f = unreal.AnimBlueprintFactory()
    say("  target_skeleton=" + str(f.get_editor_property("target_skeleton")))
except Exception as exc:
    say("  err " + str(exc))

say("=== import ui instance ===")
try:
    ui = unreal.FbxImportUI()
    say("  import_animations=" + str(ui.get_editor_property("import_animations")))
    say("  import_mesh=" + str(ui.get_editor_property("import_mesh")))
    say("  import_as_skeletal=" + str(ui.get_editor_property("import_as_skeletal")))
    say("  skeleton=" + str(ui.get_editor_property("skeleton")))
    say("  anim_class_import=" + str(ui.get_editor_property("anim_class_import")))
    say("  mesh_type_to_import=" + str(ui.get_editor_property("mesh_type_to_import")))
except Exception as exc:
    say("  err " + str(exc))

say("=== anim seq import data instance ===")
try:
    d = unreal.FbxAnimSequenceImportData()
    say("  anim_name=" + str(d.get_editor_property("anim_name")))
    say("  import_bone_tracks=" + str(d.get_editor_property("import_bone_tracks")))
except Exception as exc:
    say("  err " + str(exc))
