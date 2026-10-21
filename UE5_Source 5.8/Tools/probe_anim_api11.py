#!/usr/bin/env python3
"""Probe 11: animation-only FBX import, montage creation, montage data rows.

Hypothesis: animation-only import requires
  FbxImportUI.mesh_type_to_import = FBXIT_Animation
  FbxImportUI.automated_import_should_detect_type = False
because the automated import path otherwise re-detects the type from the FBX
and imports a static mesh (as seen in probe 10).

Output: C:\\Users\\Madi\\AppData\\Local\\Temp\\probe11_out.txt
"""
import json
import os

import unreal

OUT = r"C:\Users\Madi\AppData\Local\Temp\probe11_out.txt"
SRC = r"C:\Projects\NobleArchimedes\ArtSource\Hector\Export"
DEST = "/Game/__Probe11"
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


def snake(name):
    out = []
    for i, c in enumerate(name):
        if c.isupper() and i:
            out.append("_")
        out.append(c.lower())
    return "".join(out)


def try_prop(obj, name, value):
    for candidate in (name, snake(name)):
        try:
            obj.set_editor_property(candidate, value)
            return candidate
        except Exception:
            continue
    return None


def get_prop(obj, name, default="<unavailable>"):
    for candidate in (name, snake(name)):
        try:
            return obj.get_editor_property(candidate)
        except Exception:
            continue
    return default


unreal.EditorAssetLibrary.make_directory(DEST)

say("=== 0. FbxImportUI readable properties ===")
ui0 = unreal.FbxImportUI()
for prop in ("import_mesh", "import_as_skeletal", "import_animations",
             "import_materials", "import_textures", "import_rigid_mesh",
             "skeleton", "mesh_type_to_import", "original_import_type",
             "automated_import_should_detect_type",
             "anim_sequence_import_data", "override_animation_name",
             "create_physics_asset", "is_obj_import"):
    say("  %-42s = %r" % (prop, get_prop(ui0, prop)))

try:
    say("  FbxImportType values: %s" %
        [(n, getattr(unreal.FBXImportType, n))
         for n in dir(unreal.FBXImportType) if not n.startswith("_")])
except Exception as exc:
    say("  FbxImportType ERR %s" % exc)


say("=== 1. skeletal mesh import ===")
task = unreal.AssetImportTask()
task.set_editor_property("filename", os.path.join(SRC, "SK_Hector.fbx"))
task.set_editor_property("destination_path", DEST)
task.set_editor_property("destination_name", "SK_Hector")
task.set_editor_property("automated", True)
task.set_editor_property("replace_existing", True)
task.set_editor_property("save", True)
ui = unreal.FbxImportUI()
try_prop(ui, "import_mesh", True)
try_prop(ui, "import_as_skeletal", True)
try_prop(ui, "import_animations", False)
try_prop(ui, "import_materials", False)
try_prop(ui, "import_textures", False)
try_prop(ui, "mesh_type_to_import", unreal.FBXImportType.FBXIT_SKELETAL_MESH)
try_prop(ui, "automated_import_should_detect_type", False)
task.set_editor_property("options", ui)
TOOLS.import_asset_tasks([task])

mesh = unreal.load_asset(DEST + "/SK_Hector")
skeleton = mesh.get_editor_property("skeleton") if mesh else None
say("  mesh=%s skeleton=%s" % (mesh, skeleton))

say("=== 2. animation-only import ===")
task = unreal.AssetImportTask()
task.set_editor_property("filename", os.path.join(SRC, "A_Hector_Idle.fbx"))
task.set_editor_property("destination_path", DEST)
task.set_editor_property("destination_name", "A_Hector_Idle")
task.set_editor_property("automated", True)
task.set_editor_property("replace_existing", True)
task.set_editor_property("save", True)
ui = unreal.FbxImportUI()
try_prop(ui, "import_mesh", False)
try_prop(ui, "import_as_skeletal", True)
try_prop(ui, "import_animations", True)
try_prop(ui, "import_materials", False)
try_prop(ui, "import_textures", False)
try_prop(ui, "import_rigid_mesh", False)
try_prop(ui, "skeleton", skeleton)
try_prop(ui, "mesh_type_to_import", unreal.FBXImportType.FBXIT_ANIMATION)
try_prop(ui, "automated_import_should_detect_type", False)
anim_data = unreal.FbxAnimSequenceImportData()
try_prop(anim_data, "import_bone_tracks", True)
try_prop(ui, "anim_sequence_import_data", anim_data)
task.set_editor_property("options", ui)
TOOLS.import_asset_tasks([task])
say("  imported paths = %s" % list(task.get_editor_property("imported_object_paths")))

seq = unreal.load_asset(DEST + "/A_Hector_Idle")
say("  seq=%s class=%s" % (seq.get_path_name() if seq else None,
                           seq.get_class().get_name() if seq else None))
if seq and seq.get_class().get_name() == "AnimSequence":
    say("  length=%s frames=%s" % (get_prop(seq, "sequence_length"),
                                   get_prop(seq, "number_of_frames")))
    say("  skeleton=%s" % get_prop(seq, "skeleton"))
    say("  loop=%s" % get_prop(seq, "loop"))


say("=== 3. montage creation ===")
mont = None
if seq and seq.get_class().get_name() == "AnimSequence":
    def do_montage():
        fac = unreal.AnimMontageFactory()
        try_prop(fac, "source_animation", seq)
        try_prop(fac, "target_skeleton", skeleton)
        return TOOLS.create_asset("AM_Probe11", DEST, unreal.AnimMontage, fac)

    mont = report("create montage", do_montage)

if mont:
    say("  slot_anim_tracks=%r" % get_prop(mont, "slot_anim_tracks"))
    say("  sequence_length=%r" % get_prop(mont, "sequence_length"))
    say("  skeleton=%r" % get_prop(mont, "skeleton"))
    say("  members=%s" % [m for m in dir(mont) if not m.startswith("_")])
else:
    say("  no montage (animation import failed)")

say("=== 4. data table montage references ===")
if mont:
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
        "ComboAnimations": [DEST + "/AM_Probe11.AM_Probe11"],
        "FinalAttackAnimations": [DEST + "/AM_Probe11.AM_Probe11"],
    }]
    try:
        ok = unreal.DataTableFunctionLibrary.fill_data_table_from_json_string(
            table, json.dumps(payload))
        say("  json import with montage refs -> %s" % ok)
        if ok:
            names = list(table.get_row_names())
            say("  rows now = %s" % names)
            if "ProbeRow" in names:
                data = table.get_row("ProbeRow")
                say("  ProbeRow combo_animations = %r" %
                    (get_prop(data, "combo_animations"),))
    except Exception as exc:
        say("  json import FAIL %r" % (exc,))

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
unreal.log_warning("[PROBE11] written %d lines" % len(lines))
