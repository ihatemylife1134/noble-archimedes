#!/usr/bin/env python3
"""Probe 17: assemble an AnimGraph (SequencePlayer -> Slot -> Output) from Python."""
import unreal

OUT = r"C:\Users\Madi\AppData\Local\Temp\probe17_out.txt"
DEST = "/Game/__Probe17"
TOOLS = unreal.AssetToolsHelpers.get_asset_tools()
lines = []


def say(msg):
    lines.append(str(msg))


def report(label, fn):
    try:
        result = fn()
        say("  %s -> OK %r" % (label, result))
        return result
    except Exception as exc:
        say("  %s -> FAIL %r" % (label, exc))
        return None


unreal.EditorAssetLibrary.make_directory(DEST)
skeleton = unreal.load_asset("/Game/__Probe11/SK_Hector_Skeleton")
seq = unreal.load_asset("/Game/__Probe11/A_Hector_Idle")

fac = unreal.AnimBlueprintFactory()
fac.set_editor_property("target_skeleton", skeleton)
abp = TOOLS.create_asset("ABP_Probe17", DEST, unreal.AnimBlueprint, fac)
anim_graph = abp.get_animation_graphs()[0]
editor = unreal.BlueprintGraphEditor.get_graph_editor(anim_graph)

say("=== existing nodes in a fresh AnimGraph ===")
nodes = report("get_graph_nodes_of_class(AnimGraphNode_Base)",
               lambda: anim_graph.get_graph_nodes_of_class(unreal.AnimGraphNode_Base))
for n in nodes or []:
    say("  %s: %s" % (n.get_class().get_name(), n.get_name()))
    say("    pins out = %s" % [p.get_pin_name() for p in n.list_output_pins()])
    say("    pins in  = %s" % [p.get_pin_name() for p in n.list_input_pins()])

say("=== available Slot-ish actions ===")
available = editor.list_available_nodes([])
slot_actions = sorted(a for a in available
                      if "slot" in a.lower() or a.endswith("|Output Pose")
                      or "Root" in a)
say("  %s" % slot_actions[:40])

with open(OUT, 'w', encoding='utf-8') as fh:
    fh.write(chr(10).join(lines))
unreal.log_warning('[PROBE17] written %d lines' % len(lines))

