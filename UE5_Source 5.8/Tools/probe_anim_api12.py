#!/usr/bin/env python3
"""Probe 12: find the FBX import-type enum name and test integer assignment."""
import os

import unreal

OUT = r"C:\Users\Madi\AppData\Local\Temp\probe12_out.txt"
lines = []


def say(msg):
    lines.append(str(msg))


say("=== enum candidates ===")
for n in sorted(dir(unreal)):
    low = n.lower()
    if "fbx" in low and ("import" in low or "type" in low or "anim" in low):
        say("  " + n)

say("=== FbxImportUI mesh_type_to_import raw ===")
ui = unreal.FbxImportUI()
for prop in ("mesh_type_to_import", "original_import_type",
             "automated_import_should_detect_type"):
    try:
        val = ui.get_editor_property(prop)
        say("  %s = %r (type %s)" % (prop, val, type(val).__name__))
        say("     dir=%s" % [m for m in dir(val) if not m.startswith("_")])
    except Exception as exc:
        say("  %s ERR %s" % (prop, exc))

say("=== try integer assignment ===")
for candidate in ("mesh_type_to_import", "MeshTypeToImport"):
    for value in (2, 1, 0):
        try:
            ui.set_editor_property(candidate, value)
            say("  set %s = %d -> OK, now %r" %
                (candidate, value, ui.get_editor_property(candidate)))
        except Exception as exc:
            say("  set %s = %d -> FAIL %s" % (candidate, value, exc))

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
unreal.log_warning("[PROBE12] written %d lines" % len(lines))
