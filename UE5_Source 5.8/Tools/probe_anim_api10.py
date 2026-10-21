#!/usr/bin/env python3
"""Probe 10: montages, state-machine graph access, and montage data-table wiring.

Answers:
  A. Can a montage be created from an imported AnimSequence, with sections?
  B. Can the state-machine editor graph be reached from Python?
  C. Can state / transition nodes be added to that graph?
  D. Can a DataTable row hold UAnimMontage* array references?

Output: C:\\Users\\Madi\\AppData\\Local\\Temp\\probe10_out.txt
"""
import json
import os

import unreal

OUT = r"C:\Users\Madi\AppData\Local\Temp\probe10_out.txt"
SRC = r"C:\Projects\NobleArchimedes\ArtSource\Hector\Export"
DEST = "/Game/__Probe10"
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


def get_prop(obj, name):
    for candidate in (name, snake(name)):
        try:
            return obj.get_editor_property(candidate)
        except Exception:
            continue
    return "<unavailable>"


unreal.EditorAssetLibrary.make_directory(DEST)

# ------------------------------------------------------- A. mesh + animation
say("=== A. import mesh + animation ===")
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
task.set_editor_property("options", ui)
TOOLS.import_asset_tasks([task])

mesh = unreal.load_asset(DEST + "/SK_Hector")
skeleton = mesh.get_editor_property("skeleton") if mesh else None
say("  mesh=%s skeleton=%s" % (mesh, skeleton))

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
anim_data = unreal.FbxAnimSequenceImportData()
try_prop(anim_data, "import_bone_tracks", True)
try_prop(ui, "anim_sequence_import_data", anim_data)
task.set_editor_property("options", ui)
TOOLS.import_asset_tasks([task])

seq = unreal.load_asset(DEST + "/A_Hector_Idle")
say("  seq=%s" % (seq.get_path_name() if seq else None))
if seq:
    say("  seq length=%s frames=%s" % (
        seq.get_editor_property("sequence_length"),
        seq.get_editor_property("number_of_frames")))
    say("  seq skeleton=%s" % seq.get_editor_property("skeleton"))
    say("  seq loop=%s" % get_prop(seq, "loop"))

# ------------------------------------------------------------- B. montage
say("=== B. montage creation ===")
mont = None
if seq and skeleton:
    def do_montage():
        fac = unreal.AnimMontageFactory()
        try_prop(fac, "source_animation", seq)
        try_prop(fac, "target_skeleton", skeleton)
        return TOOLS.create_asset("AM_Probe10", DEST, unreal.AnimMontage, fac)

    mont = report("create montage", do_montage)

if mont:
    say("  slot_anim_tracks=%r" % get_prop(mont, "slot_anim_tracks"))
    say("  sequence_length=%r" % get_prop(mont, "sequence_length"))
    say("  skeleton=%r" % get_prop(mont, "skeleton"))
    say("  members=%s" % [m for m in dir(mont) if not m.startswith("_")])

# ------------------------------------------------- C. state machine graph
say("=== C. state machine graph access ===")
abp = None
if skeleton:
    def do_abp():
        fac = unreal.AnimBlueprintFactory()
        try_prop(fac, "target_skeleton", skeleton)
        return TOOLS.create_asset("ABP_Probe10", DEST, unreal.AnimBlueprint, fac)

    abp = report("create ABP", do_abp)

if abp:
    graphs = abp.get_animation_graphs()
    anim_graph = graphs[0] if graphs else None
    say("  anim graph=%s" % anim_graph)

    editor = report("get_graph_editor",
                    lambda: unreal.BlueprintGraphEditor.get_graph_editor(anim_graph))
    if editor:
        sm_node = report("create state machine node", lambda: editor.create_node_from_name(
            "Animation|StateMachines|StateMachine", unreal.Vector2D(300, 0), []))
        if sm_node:
            say("  sm node=%s" % sm_node)
            # EditorStateMachineGraph is a plain UPROPERTY (not Edit*), so it is
            # only reachable by its exact C++ name.
            for prop in ("EditorStateMachineGraph", "editorstateMachineGraph",
                         "EditorStateMachineGraph "):
                try:
                    say("  get(%r) = %r" % (prop, sm_node.get_editor_property(prop)))
                except Exception as exc:
                    say("  get(%r) ERR %s" % (prop, exc))

            # Does the blueprint expose its function graphs (state machine lives
            # there as a sub-graph)?
            try:
                all_graphs = unreal.BlueprintEditorLibrary.list_graphs(abp)
                say("  list_graphs = %s" % all_graphs)
            except Exception as exc:
                say("  list_graphs ERR %s" % exc)
            try:
                say("  abp members = %s" %
                    [m for m in dir(abp) if "graph" in m.lower()])
            except Exception:
                pass


# ------------------------------------------- D. data table with montages
say("=== D. data table montage references ===")
table = unreal.load_asset("/Game/DataTables/DT_WeaponDataTable")
if table and mont:
    row = table.get_row_names()[0]
    say("  testing row=%s" % row)

    # Try assigning the montage directly through the row struct.
    try:
        struct = table.get_row_struct()
        say("  struct=%s" % struct)
    except Exception as exc:
        say("  get_row_struct ERR %s" % exc)

    # The JSON importer path: object properties are imported via ImportText, so
    # a plain asset path string should resolve.
    payload = [{
        "Name": "ProbeRow",
        "WeaponName": "ProbeWeapon",
        "WeaponType": "Sword",
        "AttackRange": 200.0,
        "AttackSpeed": 1.0,
        "BaseDamage": 15.0,
        "DamageType": "Slash",
        "EvoCrystalColor": "Light",
        "ComboAnimCount": 3,
        "FinalAttackAnimCount": 3,
        "ComboAnimations": [DEST + "/AM_Probe10.AM_Probe10"],
        "FinalAttackAnimations": [DEST + "/AM_Probe10.AM_Probe10"],
    }]
    try:
        ok = unreal.DataTableFunctionLibrary.fill_data_table_from_json_string(
            table, json.dumps(payload))
        say("  json import with montage refs -> %s" % ok)
        if ok:
            names = list(table.get_row_names())
            say("  row names now = %s" % names)
            if "ProbeRow" in names:
                data = table.get_row("ProbeRow")
                say("  ProbeRow combo = %r" % (get_prop(data, "combo_animations"),))
    except Exception as exc:
        say("  json import FAIL %r" % (exc,))

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
