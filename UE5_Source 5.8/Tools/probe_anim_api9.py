#!/usr/bin/env python3
"""Probe 9: validate the full Hector animation pipeline end to end.

Covers:
  1. FBX skeletal-mesh import (skeleton creation).
  2. FBX animation-only import (FbxImportUI + FbxAnimSequenceImportData).
  3. AnimMontage creation from an imported AnimSequence.
  4. AnimBlueprint creation + state-machine graph authoring.
  5. DataTable row containing UAnimMontage* array references.

Results are written to C:\\Users\\Madi\\AppData\\Local\\Temp\\probe9_out.txt
"""
import os

import unreal

OUT = r"C:\Users\Madi\AppData\Local\Temp\probe9_out.txt"
lines = []
SRC = r"C:\Projects\NobleArchimedes\ArtSource\Hector\Export"
DEST = "/Game/__Probe9"

TOOLS = unreal.AssetToolsHelpers.get_asset_tools()


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


def try_prop(obj, name, value):
    """set_editor_property with a snake_case / PascalCase fallback."""
    for candidate in (name, "".join("_" + c.lower() if c.isupper() else c
                                   for c in name).lstrip("_")):
        try:
            obj.set_editor_property(candidate, value)
            return candidate
        except Exception:
            continue
    return None


unreal.EditorAssetLibrary.make_directory(DEST)

# ---------------------------------------------------------------- 1. mesh
say("=== 1. skeletal mesh import ===")


def do_mesh_import():
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
    return list(task.get_editor_property("imported_object_paths"))



# ------------------------------------------------------------ 2. animation
say("=== 2. animation import ===")


def do_anim_import():
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
    if skeleton:
        try_prop(ui, "skeleton", skeleton)
    # bImportBoneTracks lives on the anim import data, not on FbxImportUI.
    anim_data = unreal.FbxAnimSequenceImportData()
    try_prop(anim_data, "import_bone_tracks", True)
    try_prop(ui, "anim_sequence_import_data", anim_data)
    task.set_editor_property("options", ui)
    TOOLS.import_asset_tasks([task])
    return list(task.get_editor_property("imported_object_paths"))


report("anim import", do_anim_import)

seq = unreal.load_asset(DEST + "/A_Hector_Idle")
say("  seq=%s" % (seq.get_path_name() if seq else None))
if seq:
    say("  seq class=%s" % seq.get_class().get_name())
    for prop in ("sequence_length", "number_of_frames", "skeleton", "frame_rate"):
        try:
            say("  %s = %r" % (prop, seq.get_editor_property(prop)))
        except Exception as exc:
            say("  %s ERR %s" % (prop, exc))

# -------------------------------------------------------------- 3. montage
say("=== 3. montage creation ===")
mont = None
if seq and skeleton:
    def do_montage():
        fac = unreal.AnimMontageFactory()
        try_prop(fac, "source_animation", seq)
        try_prop(fac, "target_skeleton", skeleton)
        return TOOLS.create_asset("AM_Probe9", DEST, unreal.AnimMontage, fac)

    mont = report("create montage", do_montage)

if mont:
    for prop in ("slot_anim_tracks", "sequence_length", "skeleton"):
        try:
            say("  %s = %r" % (prop, mont.get_editor_property(prop)))
        except Exception as exc:
            say("  %s ERR %s" % (prop, exc))
    say("  montage members: %s" % [m for m in dir(mont) if not m.startswith("_")])

report("mesh import", do_mesh_import)

mesh = unreal.load_asset(DEST + "/SK_Hector")
skeleton = mesh.get_editor_property("skeleton") if mesh else None
say("  mesh=%s skeleton=%s" % (mesh, skeleton))
if skeleton:
    say("  skeleton class=%s" % skeleton.get_class().get_name())

# ---------------------------------------------------------- 4. AnimBP/Anim
say("=== 4. AnimBlueprint + state machine authoring ===")
abp = None
if skeleton:
    def do_abp():
        fac = unreal.AnimBlueprintFactory()
        try_prop(fac, "target_skeleton", skeleton)
        return TOOLS.create_asset("ABP_Probe9", DEST, unreal.AnimBlueprint, fac)

    abp = report("create ABP", do_abp)

if abp:
    graphs = abp.get_animation_graphs()
    say("  anim graphs = %s" % [g.get_name() for g in graphs])
    anim_graph = graphs[0] if graphs else None

    if anim_graph:
        editor = report("get_graph_editor",
                        lambda: unreal.BlueprintGraphEditor.get_graph_editor(anim_graph))
        if editor:
            try:
                available = editor.list_available_nodes([])
                say("  available node count = %d" % len(available))
                anim_nodes = [n for n in available
                              if "Animation" in n or "Sequence" in n or "State" in n]
                say("  anim-ish nodes = %s" % anim_nodes[:50])
            except Exception as exc:
                say("  list_available_nodes FAIL %r" % (exc,))

            def do_state_machine():
                return editor.create_node_from_name(
                    "Animation|StateMachines|StateMachine",
                    unreal.Vector2D(300, 0), [])

            sm_node = report("create state machine node", do_state_machine)
            if sm_node:
                say("  sm node class = %s" % sm_node.get_class().get_name())
                for prop in ("editor_state_machine_graph", "node"):
                    try:
                        say("  %s = %r" % (prop, sm_node.get_editor_property(prop)))
                    except Exception as exc:
                        say("  %s ERR %s" % (prop, exc))
                say("  sm node members = %s" %
                    [m for m in dir(sm_node) if not m.startswith("_")])

            def do_seq_player():
                return editor.create_node_from_name(
                    "Animation|Sequences|SequencePlayer",
                    unreal.Vector2D(100, 200), [])

            sp = report("create sequence player node", do_seq_player)
            if sp:
                say("  sp node class = %s" % sp.get_class().get_name())
                say("  sp members = %s" % [m for m in dir(sp) if not m.startswith("_")])

    # Direct object construction of state-machine editor nodes.
    say("=== 5. direct object construction ===")
    for cls_name in ("AnimStateNode", "AnimStateTransitionNode",
                     "AnimStateEntryNode", "AnimGraphNode_StateMachine"):
        try:
            cls = getattr(unreal, cls_name)
            obj = unreal.new_object(cls, outer=abp)
            say("  new_object(%s) -> %s" % (cls_name, obj))
            if obj:
                say("    props: %s" % [m for m in dir(obj)
                                      if "state" in m.lower() or "graph" in m.lower()])
        except Exception as exc:
            say("  new_object(%s) FAIL %r" % (cls_name, exc))

# --------------------------------------------------- 6. data table montage
say("=== 6. data table with montage references ===")
try:
    struct = unreal.load_object(None, "/Script/NobleArchimedes.WeaponData")
    say("  FWeaponData struct = %s" % struct)
    table = unreal.load_asset("/Game/DataTables/DT_WeaponDataTable")
    say("  existing weapon table = %s" % table)
    if table:
        say("  row names = %s" % list(table.get_row_names())[:5])
        struct_out = table.get_row_struct()
        say("  row struct = %s" % struct_out)
except Exception as exc:
    say("  data table probe FAIL %r" % (exc,))

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
unreal.log_warning("[PROBE9] written %d lines" % len(lines))

