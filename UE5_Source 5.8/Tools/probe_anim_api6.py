#!/usr/bin/env python3
"""Probe: can we author skeletal meshes / anim assets from Python?"""
import unreal

OUT = r"C:\Users\Madi\AppData\Local\Temp\probe6_out.txt"
lines = []


def say(msg):
    lines.append(str(msg))


for name in ("SkeletalMeshEditorSubsystem", "SkeletalMesh", "AnimSequence",
             "AnimSequenceFactory", "AnimBlueprintFactory", "AnimMontage",
             "AnimMontageFactory", "AnimationBlueprint", "Skeleton",
             "SkeletonFactory", "BlendSpaceFactory", "BlendSpace",
             "ControlRigBlueprintFactory", "PhysicsAsset", "PhysicsAssetFactory",
             "AnimMontageFactoryBase", "AnimCompositeFactory"):
    cls = getattr(unreal, name, None)
    if cls is None:
        say("MISSING " + name)
        continue
    try:
        members = sorted(m for m in dir(cls) if not m.startswith("_"))
    except Exception as exc:
        members = ["ERR " + str(exc)]
    say("=== %s ===" % name)
    say("  " + ", ".join(members))

# Any subsystem with 'skeletal' in the name
say("=== subsystems with skeletal/anim in name ===")
for n in dir(unreal):
    low = n.lower()
    if ("skeletal" in low or "anim" in low) and ("Subsystem" in n or "Library" in n):
        say("  " + n)

# AnimBlueprintFactory properties
try:
    f = unreal.AnimBlueprintFactory()
    say("=== AnimBlueprintFactory props ===")
    for p in sorted(n for n in dir(f) if not n.startswith("_")):
        say("  " + p)
except Exception as exc:
    say("err " + str(exc))

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
unreal.log_warning("[PROBE6] written %d lines" % len(lines))
