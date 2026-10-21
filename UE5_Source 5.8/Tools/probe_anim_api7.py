#!/usr/bin/env python3
"""Probe 7: montage/animBP/state-machine authoring APIs in UE 5.8."""
import unreal

OUT = r"C:\Users\Madi\AppData\Local\Temp\probe7_out.txt"
lines = []


def say(msg):
    lines.append(str(msg))


def dump(name):
    cls = getattr(unreal, name, None)
    if cls is None:
        say("MISSING " + name)
        return
    say("=== %s ===" % name)
    try:
        say("  " + ", ".join(sorted(m for m in dir(cls) if not m.startswith("_"))))
    except Exception as exc:
        say("  ERR " + str(exc))


for name in ("AnimMontage", "AnimBlueprint", "AnimBlueprintGeneratedClass",
             "AnimationStateMachineLibrary", "AnimGraphLibrary", "LinkedAnimGraphLibrary",
             "AnimationLibrary", "AnimSequenceBase", "FbxFactory", "FbxImportUI",
             "FbxSkeletalMeshImportData", "FbxAnimSequenceImportData",
             "InterchangeManager", "AssetImportTask", "SkeletalMeshImportData",
             "AnimBlueprintFactory", "AnimMontageFactory", "AnimSequenceFactory",
             "AnimCompositeFactory", "AnimSingleNodeBlueprint", "AnimSingleNodeBlueprintFactory",
             "AnimNode", "AnimNode_AssetPlayerBase", "AnimNode_SequencePlayer",
             "AnimNode_BlendSpacePlayer", "AnimNode_StateMachine", "AnimNode_Transition",
             "AnimNode_Root", "AnimInstance", "AnimationBlueprintLibrary",
             "AnimationLibrary", "EditorAssetLibrary", "SkeletalMeshUtilitiesLibrary",
             "AnimNotifyState", "AnimNotify", "AnimNotifyLibrary"):
    dump(name)

# Factory settable props that matter
for fac_name in ("AnimBlueprintFactory", "AnimMontageFactory", "AnimSequenceFactory"):
    fac = getattr(unreal, fac_name, None)
    if fac is None:
        continue
    try:
        obj = fac()
        say("--- %s instance editor props ---" % fac_name)
        for p in sorted(n for n in dir(obj) if not n.startswith("_")):
            if n in ("get_editor_property", "set_editor_property", "set_editor_properties"):
                continue
            try:
                v = obj.get_editor_property(p)
                say("   %s = %r" % (p, v))
            except Exception as exc:
                say("   %s ERR %s" % (p, exc))
    except Exception as exc:
        say("instantiate %s failed: %r" % (fac_name, exc))

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
unreal.log_warning("[PROBE7] written %d lines" % len(lines))
