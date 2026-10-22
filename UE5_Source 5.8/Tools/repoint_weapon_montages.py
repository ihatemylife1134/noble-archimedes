"""Repoint DT_WeaponData's attack montages at the new character's montages.

The rows still reference AM_Hector_* montages bound to SK_Hector_Skeleton (the
stub), which the new mesh cannot play. Uses the editor helper
UNobleDataTableAuthoring so only the two montage arrays change -- every other
field in the row is untouched.

Combat indexes ComboAnimations[Stage-1] for light stages 1-3 and
FinalAttackAnimations[Stage-1] for the finisher, so both arrays need three
entries. Only one heavy clip exists, so it fills all three finisher slots.
"""
import os

import unreal

OUT = r"C:\Users\Madi\AppData\Local\Temp\repoint_montages.txt"
TABLE_CANDIDATES = ["/Game/DataTables/DT_WeaponDataTable",
                    "/Game/DataTables/DT_WeaponData",
                    "/Game/DataTables/WeaponDataTable"]
MONTAGE_DIR = "/Game/Characters/HectorBase/Montages"

COMBO = ["%s/AM_HectorBase_Light1" % MONTAGE_DIR,
         "%s/AM_HectorBase_Light2" % MONTAGE_DIR,
         "%s/AM_HectorBase_Light3" % MONTAGE_DIR]
FINAL = ["%s/AM_HectorBase_Heavy" % MONTAGE_DIR] * 3
lines = []


def say(m):
    lines.append(str(m))


try:
    table = None
    for path in TABLE_CANDIDATES:
        if unreal.EditorAssetLibrary.does_asset_exist(path):
            table = unreal.EditorAssetLibrary.load_asset(path)
            say("table = %s" % path)
            break
    if not table:
        raise RuntimeError("DT_WeaponData not found at %s" % TABLE_CANDIDATES)

    rows = unreal.NobleDataTableAuthoring.get_row_names(table)
    say("rows = %d" % len(rows))

    failures = 0
    for row in rows:
        error = unreal.NobleDataTableAuthoring.set_weapon_row_montages(
            table, row, COMBO, FINAL)
        if error:
            failures += 1
            say("  %-24s %s" % (row, error))
    say("applied to %d rows, %d reported problems" % (len(rows), failures))

    say("")
    say("--- read back ---")
    for row in rows[:4]:
        say("  %-24s %s" % (row, unreal.NobleDataTableAuthoring.describe_weapon_row_montages(
            table, row)))

    say("")
    say("saved = %s" % unreal.EditorAssetLibrary.save_loaded_asset(
        table, only_if_is_dirty=False))
except Exception as exc:
    say("FAILED: %s" % exc)

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
unreal.log("[NA-REPOINTMONTAGES] wrote %d lines" % len(lines))
