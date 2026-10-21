#!/usr/bin/env python3
"""Probe 14: verify montage object references resolve in a DataTable row."""
import json

import unreal

OUT = r"C:\Users\Madi\AppData\Local\Temp\probe14_out.txt"
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


mont = unreal.load_asset("/Game/__Probe11/AM_Probe11")
seq = unreal.load_asset("/Game/__Probe11/A_Hector_Idle")
say("mont=%s seq=%s" % (mont, seq))
if mont:
    say("  num sections = %s" % mont.get_num_sections())
    say("  section 0 name = %r" % mont.get_section_name(0))
    say("  play length = %s" % mont.get_play_length())
    say("  group name = %r" % mont.get_group_name())
    say("  slot_anim_tracks = %r" % mont.get_editor_property("slot_anim_tracks"))

say("=== data table montage reference round trip ===")
table = unreal.load_asset("/Game/DataTables/DT_WeaponDataTable")
payload = [{
    "Name": "ProbeRow",
    "WeaponName": "ProbeWeapon",
    "WeaponType": "Sword",
    "AttackRange": 200.0,
    "AttackSpeed": 1.0,
    "BaseDamage": 15.0,
    "DamageType": "Slash",
    "EvoCrystalColor": "Light",
    "ComboAnimCount": 1,
    "FinalAttackAnimCount": 1,
    "ComboAnimations": ["/Game/__Probe11/AM_Probe11.AM_Probe11"],
    "FinalAttackAnimations": ["/Game/__Probe11/AM_Probe11.AM_Probe11"],
}]
ok = report("fill from json", lambda: unreal.DataTableFunctionLibrary.
            fill_data_table_from_json_string(table, json.dumps(payload)))
if ok:
    say("  rows = %s" % list(table.get_row_names()))
    row = report("get_data_table_row_from_name", lambda:
                 unreal.DataTableFunctionLibrary.get_data_table_row_from_name(
                     table, "ProbeRow"))
    if row:
        say("  row object = %r" % (row,))
        for prop in ("combo_animations", "final_attack_animations",
                     "weapon_name", "combo_anim_count"):
            try:
                say("    %s = %r" % (prop, row.get_editor_property(prop)))
            except Exception as exc:
                say("    %s ERR %s" % (prop, exc))
    exported = report("export to json", lambda:
                      unreal.DataTableFunctionLibrary.export_data_table_to_json_string(table))
    if exported:
        say("  export = %s" % exported[:800])

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
unreal.log_warning("[PROBE14] written %d lines" % len(lines))
