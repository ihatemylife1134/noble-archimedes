#!/usr/bin/env python3
"""Probe 15: montage save + reference resolution, and state graph authoring."""
import json

import unreal

OUT = r"C:\Users\Madi\AppData\Local\Temp\probe15_out.txt"
DEST = "/Game/__Probe15"
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

say("=== 1. montage: create, save, and reference from a data table ===")
skeleton = unreal.load_asset("/Game/__Probe11/SK_Hector_Skeleton")
seq = unreal.load_asset("/Game/__Probe11/A_Hector_Idle")
fac = unreal.AnimMontageFactory()
fac.set_editor_property("source_animation", seq)
fac.set_editor_property("target_skeleton", skeleton)
mont = report("create montage", lambda: TOOLS.create_asset(
    "AM_Probe15", DEST, unreal.AnimMontage, fac))
if mont:
    say("  num sections = %s" % mont.get_num_sections())
    say("  section 0 = %r" % mont.get_section_name(0))
    say("  play length = %s" % mont.get_play_length())
    report("save montage", lambda: unreal.EditorAssetLibrary.save_loaded_asset(
        mont, only_if_is_dirty=False))
    say("  resaved -> %s" % unreal.EditorAssetLibrary.does_asset_exist(
        DEST + "/AM_Probe15"))

    table = unreal.load_asset("/Game/DataTables/DT_WeaponDataTable")
    payload = [{
        "Name": "ProbeRow",
        "WeaponName": "ProbeWeapon",
        "WeaponType": "Sword",
        "AttackRange": 200.0, "AttackSpeed": 1.0, "BaseDamage": 15.0,
        "DamageType": "Slash", "EvoCrystalColor": "Light",
        "ComboAnimCount": 1, "FinalAttackAnimCount": 1,
        "ComboAnimations": [DEST + "/AM_Probe15.AM_Probe15"],
        "FinalAttackAnimations": [DEST + "/AM_Probe15.AM_Probe15"],
    }]
    report("fill json", lambda: unreal.DataTableFunctionLibrary.
           fill_data_table_from_json_string(table, json.dumps(payload)))
    exported = report("export json", lambda: unreal.DataTableFunctionLibrary.
                      export_data_table_to_json_string(table))
    if exported:
        data = json.loads(exported)
        for row in data:
            say("  %s combo=%r" % (row.get("Name"), row.get("ComboAnimations")))

say("=== 2. state machine graph authoring ===")
fac2 = unreal.AnimBlueprintFactory()
fac2.set_editor_property("target_skeleton", skeleton)
abp = report("create ABP", lambda: TOOLS.create_asset(
    "ABP_Probe15", DEST, unreal.AnimBlueprint, fac2))
if abp:
    anim_graph = abp.get_animation_graphs()[0]
    editor = unreal.BlueprintGraphEditor.get_graph_editor(anim_graph)

    # Which anim graph node categories are registered?
    available = editor.list_available_nodes([])
    anim_actions = sorted(a for a in available if a.startswith("Animation|"))
    say("  Animation|* actions = %s" % anim_actions)

    sm_node = report("create state machine node", lambda: editor.create_node_from_name(
        "Animation|StateMachines|StateMachine", unreal.Vector2D(300, 0), []))

    # The state machine's own graph is a sub-graph of the AnimBlueprint.
    for prop in ("FunctionGraphs", "function_graphs", "AnimGraphs",
                 "anim_graphs", "VariableGraphs"):
        try:
            val = abp.get_editor_property(prop)
            say("  abp.get(%r) = %r" % (prop, val))
        except Exception as exc:
            say("  abp.get(%r) ERR %s" % (prop, exc))

    try:
        say("  list_graphs = %s" % unreal.BlueprintEditorLibrary.list_graphs(abp))
    except Exception as exc:
        say("  list_graphs ERR %s" % exc)

    # Does the AnimBlueprint expose a helper to get the state machine graph?
    say("  abp members with 'graph'/'machine' = %s" %
        [m for m in dir(abp) if "graph" in m.lower() or "machine" in m.lower()])
    say("  unreal members with 'StateMachine' = %s" %
        [m for m in dir(unreal) if "StateMachine" in m or "AnimState" in m])

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
unreal.log_warning("[PROBE15] written %d lines" % len(lines))
