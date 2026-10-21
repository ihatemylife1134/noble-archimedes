#!/usr/bin/env python3
"""Probe 13: verify montage refs resolve + reach the state machine graph."""
import json

import unreal

OUT = r"C:\Users\Madi\AppData\Local\Temp\probe13_out.txt"
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


say("=== 1. do montage refs resolve in the data table? ===")
table = unreal.load_asset("/Game/DataTables/DT_WeaponDataTable")
if table:
    out = unreal.DataTableFunctionLibrary.export_data_table_to_json_string(table)
    data = json.loads(out)
    for row in data:
        say("  row %s:" % row.get("Name"))
        for key in ("ComboAnimations", "FinalAttackAnimations"):
            say("    %s = %r" % (key, row.get(key)))

say("=== 2. state machine graph access (exact property case) ===")
skeleton = unreal.load_asset("/Game/__Probe11/SK_Hector_Skeleton")
fac = unreal.AnimBlueprintFactory()
fac.set_editor_property("target_skeleton", skeleton)
abp = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
    "ABP_Probe13", "/Game/__Probe13", unreal.AnimBlueprint, fac)
say("  abp = %s" % abp)
if abp:
    graphs = abp.get_animation_graphs()
    anim_graph = graphs[0] if graphs else None
    editor = unreal.BlueprintGraphEditor.get_graph_editor(anim_graph)
    sm_node = report("create state machine node", lambda: editor.create_node_from_name(
        "Animation|StateMachines|StateMachine", unreal.Vector2D(300, 0), []))

    if sm_node:
        for prop in ("EditorStateMachineGraph", "OwnerAnimGraphNode",
                     "editor_state_machine_graph"):
            try:
                val = sm_node.get_editor_property(prop)
                say("  sm.get(%r) = %r" % (prop, val))
            except Exception as exc:
                say("  sm.get(%r) ERR %s" % (prop, exc))

        # Can we make a state machine graph ourselves and assign it?
        smg_cls = getattr(unreal, "AnimationStateMachineGraph", None)
        say("  AnimationStateMachineGraph class = %s" % smg_cls)
        if smg_cls:
            smg = report("new_object AnimationStateMachineGraph",
                         lambda: unreal.new_object(smg_cls, outer=sm_node))
            if smg:
                say("  smg members = %s" %
                    [m for m in dir(smg) if not m.startswith("_")])
                for prop in ("EntryNode", "OwnerAnimGraphNode", "Nodes"):
                    try:
                        say("  smg.get(%r) = %r" % (prop, smg.get_editor_property(prop)))
                    except Exception as exc:
                        say("  smg.get(%r) ERR %s" % (prop, exc))

    # What does the anim graph contain?
    try:
        nodes = anim_graph.get_graph_nodes_of_class(unreal.EdGraphNode)
        say("  anim graph nodes = %s" %
            [(n.get_class().get_name(), n.get_name()) for n in nodes])
    except Exception as exc:
        say("  get_graph_nodes_of_class ERR %s" % exc)

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
unreal.log_warning("[PROBE13] written %d lines" % len(lines))
