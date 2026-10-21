#!/usr/bin/env python3
"""Probe graph-editing helpers. Writes results to a file for fast, reliable reading."""
import unreal

OUT = r"C:\Users\Madi\AppData\Local\Temp\probe5_out.txt"
lines = []


def say(msg):
    lines.append(str(msg))


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
                or "new_graph" in low or "add_graph" in low
                or "add_slot" in low or "add_montage" in low
                or "add_variable" in low or "add_function" in low):
            hits.append("%s.%s" % (n, m))
say("HITS=" + ", ".join(sorted(set(hits))))

for cls_name in ("AnimationBlueprintLibrary", "AnimGraphLibrary", "BlueprintEditorLibrary",
                 "KismetEditorUtilities", "AnimationStateGraph", "AnimationGraph",
                 "AnimBlueprintGeneratedClass", "AnimGraphLibrary", "SlotManager",
                 "AnimationLibrary", "EditorSkeletalMeshLibrary"):
    cls = getattr(unreal, cls_name, None)
    if cls is None:
        say("MISSING " + cls_name)
        continue
    try:
        members = sorted(m for m in dir(cls) if not m.startswith("_"))
    except Exception as exc:
        members = ["ERR " + str(exc)]
    say("=== %s ===" % cls_name)
    say("  " + ", ".join(members))

# Does an AnimBlueprint support adding nodes via BlueprintEditorLibrary?
try:
    bel = unreal.BlueprintEditorLibrary
    say("=== BlueprintEditorLibrary statics ===")
    for m in sorted(n for n in dir(bel) if not n.startswith("_")):
        say("  " + m)
except Exception as exc:
    say("err " + str(exc))

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
unreal.log_warning("[PROBE5] written %d lines" % len(lines))
