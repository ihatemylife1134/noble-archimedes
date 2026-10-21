#!/usr/bin/env python3
"""Probe the UE 5.8 Python API for FBX import + animation blueprint factories."""
import unreal


def say(msg):
    unreal.log_warning("[PROBE] " + str(msg))


names = dir(unreal)
interesting = [n for n in names if any(k in n for k in (
    "Fbx", "Interchange", "AnimBlueprint", "AnimMontage", "AnimSequence",
    "SkeletalMesh", "AnimationBlueprint", "AnimGraph", "Skeleton", "AnimationAsset"))]
say("INTERESTING=" + ", ".join(sorted(interesting)))

for cls_name in ("FbxFactory", "FbxImportUI", "FbxSkeletalMeshImportData",
                 "FbxAnimSequenceImportData", "FbxAnimSequenceFactory",
                 "AnimBlueprintFactory", "AnimationBlueprintFactory",
                 "AnimMontageFactory", "SkeletalMeshFactory", "AnimSequenceFactory"):
    cls = getattr(unreal, cls_name, None)
    if cls is None:
        say("MISSING " + cls_name)
        continue
    props = []
    try:
        for p in unreal.SystemLibrary.get_class_default_object(cls) if False else []:
            pass
    except Exception:
        pass
    say("FOUND %s -> %s" % (cls_name, cls))
    try:
        say("   props: " + ", ".join(sorted(
            [p for p in dir(cls) if not p.startswith("_")])[:60]))
    except Exception as exc:
        say("   err " + str(exc))

try:
    iu = unreal.FbxImportUI()
    say("FbxImportUI ok, anim_import " + str(iu.get_editor_property("import_animations")))
except Exception as exc:
    say("FbxImportUI fail " + str(exc))
