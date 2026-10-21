#!/usr/bin/env python3
"""Probe 8: graph node class census + real FBX import / montage / AnimBP pipeline."""
import os
import unreal

OUT = r"C:\Users\Madi\AppData\Local\Temp\probe8_out.txt"
lines = []


def say(msg):
    lines.append(str(msg))


say("=== classes containing GraphNode / EdGraph / K2Node ===")
for n in sorted(dir(unreal)):
    if ("GraphNode" in n) or n.startswith("EdGraph") or ("K2Node" in n):
        say("  " + n)

say("=== anim graph node classes ===")
for n in sorted(dir(unreal)):
    low = n.lower()
    if low.startswith("animgraphnode") or low.startswith("animnode"):
        say("  " + n)

say("=== state machine classes ===")
for n in sorted(dir(unreal)):
    if "StateMachine" in n or "AnimStateMachine" in n:
        say("  " + n)

say("=== factory classes ===")
for n in sorted(dir(unreal)):
    if n.endswith("Factory"):
        say("  " + n)

SRC = r"C:\Projects\NobleArchimedes\ArtSource\Hector\Export"
DEST = "/Game/__Probe"
unreal.EditorAssetLibrary.make_directory(DEST)


def asset_tools():
    return unreal.AssetToolsHelpers.get_asset_tools()


def report(label, fn):
    try:
        result = fn()
        say("  %s -> OK %r" % (label, result))
        return result
    except Exception as exc:
        say("  %s -> FAIL %r" % (label, exc))
        return None


say("=== FbxImportUI properties ===")
try:
    ui = unreal.FbxImportUI()
    skip = ("get_editor_property", "set_editor_property", "set_editor_properties",
            "get_class", "get_default_object", "static_class", "get_fname",
            "get_full_name", "get_name", "get_outer", "get_outermost", "get_package",
            "get_path_name", "get_typed_outer", "get_world", "modify", "rename",
            "reset_editor_property", "is_editor_property_overridden",
            "is_package_external", "call_method", "cast",
            "acquire_editor_element_handle")
    for p in sorted(dir(ui)):
        if p.startswith("_") or p in skip:
            continue
        try:
            say("   %s = %r" % (p, ui.get_editor_property(p)))
        except Exception as exc:
            say("   %s ERR %s" % (p, exc))
except Exception as exc:
    say("FbxImportUI fail " + repr(exc))


say("=== import SK_Hector.fbx (skeletal mesh + skeleton) ===")


def do_mesh_import():
    task = unreal.AssetImportTask()
    task.set_editor_property("filename", os.path.join(SRC, "SK_Hector.fbx"))
    task.set_editor_property("destination_path", DEST)
    task.set_editor_property("destination_name", "SK_Hector")
    task.set_editor_property("automated", True)
    task.set_editor_property("replace_existing", True)
    task.set_editor_property("save", True)
    ui = unreal.FbxImportUI()
    ui.set_editor_property("import_mesh", True)
    ui.set_editor_property("import_as_skeletal", True)
    ui.set_editor_property("import_animations", False)
    ui.set_editor_property("import_materials", True)
    ui.set_editor_property("import_textures", False)
    task.set_editor_property("options", ui)
    asset_tools().import_asset_tasks([task])
    return list(task.get_editor_property("imported_object_paths"))


report("mesh import", do_mesh_import)

mesh = unreal.load_asset(DEST + "/SK_Hector")
skeleton = None
if mesh:
    say("  mesh class %s" % mesh.get_class().get_name())
    try:
        skeleton = mesh.get_editor_property("skeleton")
        say("  skeleton = %s" % (skeleton.get_path_name() if skeleton else None))
    except Exception as exc:
        say("  skeleton ERR %s" % exc)
else:
    say("  mesh missing")

skel_asset = None
if skeleton:
    skel_asset = unreal.load_object(None, skeleton.get_path_name())
    say("  skeleton asset = %s" % (skel_asset.get_path_name() if skel_asset else None))
else:
    assets = unreal.EditorAssetLibrary.list_assets(DEST, recursive=True)
    say("  assets in probe dir = %s" % list(assets))
    for a in assets:
        try:
            o = unreal.load_asset(a)
            say("    %s -> %s" % (a, o.get_class().get_name() if o else None))
        except Exception:
            pass


say("=== import A_Hector_Idle.fbx as animation ===")


def do_anim_import():
    task = unreal.AssetImportTask()
    task.set_editor_property("filename", os.path.join(SRC, "A_Hector_Idle.fbx"))
    task.set_editor_property("destination_path", DEST)
    task.set_editor_property("destination_name", "A_Hector_Idle")
    task.set_editor_property("automated", True)
    task.set_editor_property("replace_existing", True)
    task.set_editor_property("save", True)
    ui = unreal.FbxImportUI()
    ui.set_editor_property("import_mesh", False)
    ui.set_editor_property("import_as_skeletal", True)
    ui.set_editor_property("import_animations", True)
    ui.set_editor_property("import_bone_tracks", True)
    if skel_asset:
        ui.set_editor_property("skeleton", skel_asset)
    task.set_editor_property("options", ui)
    asset_tools().import_asset_tasks([task])
    return list(task.get_editor_property("imported_object_paths"))


report("anim import", do_anim_import)

seq = unreal.load_asset(DEST + "/A_Hector_Idle")
say("  seq = %s (%s)" % (seq.get_path_name() if seq else None,
                         seq.get_class().get_name() if seq else "-"))
if seq:
    try:
        say("  seq length = %s" % seq.get_editor_property("sequence_length"))
    except Exception as exc:
        say("  seq length ERR %s" % exc)
    try:
        say("  seq skeleton = %s" % seq.get_editor_property("skeleton").get_path_name())
    except Exception as exc:
        say("  seq skeleton ERR %s" % exc)


say("=== create montage ===")
mont = None
if seq and skel_asset:
    fac = unreal.AnimMontageFactory()
    try:
        fac.set_editor_property("source_animation", seq)
    except Exception as exc:
        say("  set source_animation ERR %s" % exc)
    try:
        fac.set_editor_property("target_skeleton", skel_asset)
    except Exception as exc:
        say("  set target_skeleton ERR %s" % exc)
    mont = report("create montage", lambda: asset_tools().create_asset(
        "AM_Probe", DEST, unreal.AnimMontage, fac))
if mont:
    try:
        say("  num sections = %s" % mont.get_num_sections())
    except Exception as exc:
        say("  num sections ERR %s" % exc)
    try:
        say("  slot_anim_tracks = %r" % (mont.get_editor_property("slot_anim_tracks"),))
    except Exception as exc:
        say("  slot_anim_tracks ERR %s" % exc)
    try:
        say("  members w/ section = %s" % [m for m in dir(mont) if "section" in m.lower()])
    except Exception:
        pass

say("=== create AnimBlueprint ===")
abp = None
if skel_asset:
    fac2 = unreal.AnimBlueprintFactory()
    try:
        fac2.set_editor_property("target_skeleton", skel_asset)
    except Exception as exc:
        say("  set target_skeleton ERR %s" % exc)
    abp = report("create ABP", lambda: asset_tools().create_asset(
        "ABP_Probe", DEST, unreal.AnimBlueprint, fac2))
if abp:
    try:
        graphs = abp.get_animation_graphs()
        say("  anim graphs = %s" % [(g.get_name() if g else None) for g in graphs])
        for g in graphs:
            if g is None:
                continue
            say("   graph class %s" % g.get_class().get_name())
            say("   graph members = %s" % [m for m in dir(g) if not m.startswith("_")][:80])
    except Exception as exc:
        say("  anim graphs ERR %s" % exc)
    try:
        nodes = abp.get_nodes_of_class(unreal.AnimNode_StateMachine)
        say("  state machine nodes = %d" % len(nodes))
        for n in nodes:
            say("   %s" % n.get_name())
            say("   members = %s" % [m for m in dir(n) if not m.startswith("_")])
    except Exception as exc:
        say("  get_nodes_of_class ERR %s" % exc)
    try:
        say("  generated_class = %s" % abp.generated_class)
    except Exception as exc:
        say("  generated_class ERR %s" % exc)

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
unreal.log_warning("[PROBE8] written %d lines" % len(lines))
