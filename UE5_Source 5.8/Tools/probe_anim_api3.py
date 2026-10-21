#!/usr/bin/env python3
"""Probe AnimBP graph-authoring API in UE 5.8."""
import unreal


def say(msg):
    unreal.log_warning("[PROBE3] " + str(msg))


graphy = sorted(n for n in dir(unreal) if "Graph" in n)
say("GRAPH_NAMES=" + ", ".join(graphy))

animy = sorted(n for n in dir(unreal) if "AnimationBlueprint" in n or "AnimBlueprint" in n)
say("ABP_NAMES=" + ", ".join(animy))

for cls_name in ("AnimBlueprint", "AnimBlueprintGeneratedClass", "AnimationBlueprintLibrary",
                 "AnimGraphNode", "AnimGraphNode_StateMachine", "AnimGraphNode_SequencePlayer",
                 "AnimGraphNode_Slot", "AnimGraphNode_Transition", "AnimStateMachineBlueprintLibrary",
                 "AnimNode_AssetPlayerBase", "AnimationStateMachineLibrary", "AnimBlueprintEditorLibrary"):
    cls = getattr(unreal, cls_name, None)
    if cls is None:
        say("MISSING " + cls_name)
        continue
    try:
        members = sorted(n for n in dir(cls) if not n.startswith("_"))
    except Exception as exc:
        members = ["ERR " + str(exc)]
    say("=== %s === %s" % (cls_name, ", ".join(members)))

say("=== AnimBlueprint instance props ===")
try:
    abp = unreal.AnimBlueprint()
    for p in sorted(n for n in dir(abp) if not n.startswith("_")):
        say("  " + p)
except Exception as exc:
    say("  err " + str(exc))
