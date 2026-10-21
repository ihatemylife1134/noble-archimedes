#!/usr/bin/env python3
"""Probe graph-editing helper functions in UE 5.8."""
import unreal


def say(msg):
    unreal.log_warning("[PROBE4] " + str(msg))


# 1. all *Library classes
libs = sorted(n for n in dir(unreal) if n.endswith("Library"))
say("LIBS=" + ", ".join(libs))

# 2. any unreal attribute containing add_node / add_state / add_transition
hits = []
for n in dir(unreal):
    try:
        obj = getattr(unreal, n)
    except Exception:
        continue
    try:
        members = dir(obj)
    except Exception:
        continue
    for m in members:
        low = m.lower()
        if ("add_node" in low or "add_state" in low or "add_transition"
                or "add_anim" in low or "new_graph" in low or "add_graph"
                or "add_slot" in low or "add_montage" in low):
            hits.append("%s.%s" % (n, m))
say("HITS=" + ", ".join(sorted(set(hits))))

for cls_name in ("AnimationBlueprintLibrary", "AnimGraphLibrary", "BlueprintEditorLibrary",
                 "KismetEditorUtilities", "AnimationStateGraph", "AnimationGraph",
                 "AnimBlueprintGeneratedClass", "AnimationStateMachineBlueprintLibrary"):
    cls = getattr(unreal, cls_name, None)
    if cls is None:
        say("MISSING " + cls_name)
        continue
    try:
        members = sorted(m for m in dir(cls) if not m.startswith("_"))
    except Exception as exc:
        members = ["ERR " + str(exc)]
    say("=== %s === %s" % (cls_name, ", ".join(members)))

# 3. AnimBlueprint full member list (truncated earlier)
try:
    abp = unreal.AnimBlueprint()
    say("=== AnimBlueprint members ===")
    for p in sorted(n for n in dir(abp) if not n.startswith("_")):
        say("  " + p)
except Exception as exc:
    say("  err " + str(exc))

# 4. Montage-related: check AnimMontageFactory usage
try:
    f = unreal.AnimMontageFactory()
    say("=== AnimMontageFactory ===")
    for p in sorted(n for n in dir(f) if not n.startswith("_")):
        say("  " + p)
except Exception as exc:
    say("  err " + str(exc))
