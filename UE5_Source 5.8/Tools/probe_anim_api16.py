#!/usr/bin/env python3
"""Probe 16: can we author states inside the state machine graph?"""
import unreal

OUT = r"C:\Users\Madi\AppData\Local\Temp\probe16_out.txt"
DEST = "/Game/__Probe16"
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
abp = TOOLS.create_asset("ABP_Probe16", DEST, unreal.AnimBlueprint, fac)
anim_graph = abp.get_animation_graphs()[0]
editor = unreal.BlueprintGraphEditor.get_graph_editor(anim_graph)
sm_node = editor.create_node_from_name(
    "Animation|StateMachines|StateMachine", unreal.Vector2D(300, 0), [])
say("sm_node = %s" % sm_node)

say("=== 1. find the state machine graph ===")
graphs = unreal.BlueprintEditorLibrary.list_graphs(abp)
smg = None
for g in graphs:
    say("  graph: %r" % (g,))
    name = g.get_name() if hasattr(g, "get_name") else str(g)
    cls_name = g.get_class().get_name() if hasattr(g, "get_class") else "?"
    say("    class = %s name = %s" % (cls_name, name))
    if cls_name == "AnimationStateMachineGraph":
        smg = g
say("  smg = %s" % smg)

if smg:
    nodes = report("get Nodes", lambda: smg.get_editor_property("Nodes"))
    say("  nodes = %r" % (nodes,))
    for prop in ("EntryNode", "OwnerAnimGraphNode", "Schema", "SubGraphs"):
        try:
            say("  smg.%s = %r" % (prop, smg.get_editor_property(prop)))
        except Exception as exc:
            say("  smg.%s ERR %s" % (prop, exc))

    say("=== 2. can we create an AnimStateNode and add it? ===")
    state = report("new_object AnimStateNode",
                   lambda: unreal.new_object(unreal.AnimStateNode, outer=smg))
    if state:
        say("  state = %s" % state)
        for prop in ("BoundGraph", "StateType", "bAlwaysResetOnEntry"):
            try:
                say("    state.%s = %r" % (prop, state.get_editor_property(prop)))
            except Exception as exc:
                say("    state.%s ERR %s" % (prop, exc))
        say("    state members = %s" %
            [m for m in dir(state) if not m.startswith("_")])

    say("=== 3. can we add nodes to the graph Nodes array? ===")
    if state:
        try:
            arr = list(smg.get_editor_property("Nodes"))
            arr.append(state)
            smg.set_editor_property("Nodes", arr)
            say("  after set Nodes = %r" % (smg.get_editor_property("Nodes"),))
        except Exception as exc:
            say("  set Nodes FAIL %s" % exc)

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
unreal.log_warning("[PROBE16] written %d lines" % len(lines))
