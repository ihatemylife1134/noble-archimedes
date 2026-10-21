#!/usr/bin/env python3
"""Run only the Hector animation pipeline step from ue5_build_content."""
import os
import sys

import unreal

sys.path.insert(0, r"C:\Projects\NobleArchimedes\Tools")

import ue5_build_content as build  # noqa: E402  (main() is __main__-guarded)

OUT = r"C:\Users\Madi\AppData\Local\Temp\anim_step_out.txt"
lines = []


def say(msg):
    lines.append(str(msg))


ok = build.build_hector_animation()
say("build_hector_animation -> %s" % ok)
say("errors = %d" % build.STATS["errors"])
for message in build.ERRORS:
    say("ERROR: " + message)
say("created=%d updated=%d" % (build.STATS["created"], build.STATS["updated"]))

for anim in build.HECTOR_ANIMATIONS:
    seq = unreal.EditorAssetLibrary.does_asset_exist(build.hector_sequence_path(anim))
    mont = unreal.EditorAssetLibrary.does_asset_exist(build.hector_montage_path(anim))
    say("  %-12s seq=%s montage=%s" % (anim, seq, mont))

combo, finisher = build.weapon_montage_refs("Sword")
say("Sword combo = %s" % combo)
say("Sword finisher = %s" % finisher)
combo, finisher = build.weapon_montage_refs("Special")
say("Special combo = %s" % combo)

abp = unreal.load_asset(build.asset_path(build.HECTOR_DIR, build.HECTOR_ANIMBP_NAME))
say("AB_Hector = %s" % abp)
if abp:
    say("  generated class = %s" % abp.generated_class())
    graphs = abp.get_animation_graphs()
    if graphs:
        nodes = graphs[0].get_graph_nodes_of_class(unreal.AnimGraphNode_Base)
        for n in nodes:
            say("  node %s" % n.get_class().get_name())
            for pin in n.list_input_pins():
                try:
                    linked = [p.get_owning_node().get_class().get_name()
                              for p in pin.list_connected_pins()]
                except Exception as exc:
                    linked = ["ERR %s" % exc]
                say("    in  %-8s <- %s" % (pin.get_pin_name(), linked))

say("=== weapon data table wiring ===")
build.import_data_table("WeaponDataTable.csv", "FWeaponData", "DT_WeaponDataTable")
table = unreal.load_asset("/Game/DataTables/DT_WeaponDataTable")
if table:
    exported = unreal.DataTableFunctionLibrary.export_data_table_to_json_string(table)
    import json
    rows = json.loads(exported)
    say("rows = %d" % len(rows))
    for row in rows[:2] + [r for r in rows if r.get("WeaponName") == "Shuriken"]:
        say("  %s type=%s combo=%s final=%s" % (
            row.get("WeaponName"), row.get("WeaponType"),
            row.get("ComboAnimations"), row.get("FinalAttackAnimations")))

lib = getattr(unreal, "NobleAnimGraphAuthoring", None)
abp = unreal.load_asset(build.asset_path(build.HECTOR_DIR, build.HECTOR_ANIMBP_NAME))
if lib and abp:
    machine = lib.get_or_create_state_machine(abp, "Locomotion")
    names = [str(n) for n in lib.get_state_names(machine)]
    say("state machine graph = %s" % machine)
    say("states (%d) = %s" % (len(names), sorted(names)))
    say("transitions = %d" % lib.get_transition_count(machine))
    missing = sorted(set(build.HECTOR_STATE_CLIPS) - set(names))
    if missing:
        say("MISSING STATES = %s" % missing)

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
unreal.log_warning("[ANIMSTEP] written %d lines" % len(lines))
