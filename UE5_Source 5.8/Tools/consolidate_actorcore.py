"""Consolidate the ActorCore clips: keep only the trimmed ones, rewire the states.

State of the folder before this runs:
  AC_Idle                              trimmed, 171 frames   <- keep
  AC_Walk_Loop*                        not yet imported      <- import
  AC_Idle*0_Open_A_UE5                 reference pose, junk  <- delete
  AC_Walk_*0_Open_A_UE5                reference pose, junk  <- delete
  AC_Idlemale-idle_279398              900 frames, padded    <- delete
  AC_Walk_*walk-relaxed-*.uasset       900 frames, padded    <- delete

The padded clips animate for ~6 seconds and then hold still, which is the freeze
reported in game. The trimmed clips contain only the motion.
"""
import os

import unreal

OUT = r"C:\Users\Madi\AppData\Local\Temp\consolidate_actorcore.txt"
DIR = "/Game/Characters/HectorBase/ActorCore"
ABP = "/Game/Characters/HectorBase/AB_HectorBaseV2"
SKELETON = "/Game/Characters/HectorBase/survival_character_Skeleton"
TRIMMED = r"C:\Projects\NobleArchimedes\ArtSource\ActorCore\Trimmed"

# Keep the trimmed assets; everything else in the folder is a padded duplicate or
# a reference pose.
KEEP = {"AC_Idle", "AC_Walk_Loop"}
IMPORT = [("AC_Walk_Loop.fbx", "AC_Walk_Loop")]
lines = []


def say(m):
    lines.append(str(m))


def load(path):
    return unreal.EditorAssetLibrary.load_asset(path) if \
        unreal.EditorAssetLibrary.does_asset_exist(path) else None


def import_anim(fbx, name):
    task = unreal.AssetImportTask()
    task.set_editor_property("filename", fbx)
    task.set_editor_property("destination_path", DIR)
    task.set_editor_property("destination_name", name)
    task.set_editor_property("automated", True)
    task.set_editor_property("replace_existing", True)
    task.set_editor_property("save", True)

    options = unreal.FbxImportUI()
    options.set_editor_property("import_mesh", False)
    options.set_editor_property("import_animations", True)
    options.set_editor_property("import_as_skeletal", False)
    options.set_editor_property("import_materials", False)
    options.set_editor_property("import_textures", False)
    options.set_editor_property("skeleton", load(SKELETON))
    task.set_editor_property("options", options)

    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    return unreal.EditorAssetLibrary.does_asset_exist("%s/%s" % (DIR, name))


try:
    # --- 1. import the trimmed walk loop ---------------------------------
    for fbx_name, asset_name in IMPORT:
        full = os.path.join(TRIMMED, fbx_name)
        if not os.path.exists(full):
            say("%s MISSING on disk" % fbx_name)
            continue
        say("importing %s -> %s" % (fbx_name, import_anim(full, asset_name)))

    # --- 2. delete everything that is not a trimmed clip ------------------
    say("")
    for path in unreal.EditorAssetLibrary.list_assets(DIR, recursive=False):
        name = path.split("/")[-1].split(".")[0]
        if name in KEEP:
            say("keep   %s" % name)
            continue
        say("delete %-40s %s" % (name, unreal.EditorAssetLibrary.delete_asset(path)))

    unreal.EditorAssetLibrary.save_directory(DIR, only_if_is_dirty=False, recursive=True)

    # --- 3. rewire the locomotion states ---------------------------------
    say("")
    abp = load(ABP)
    sm = unreal.NobleAnimGraphAuthoring.get_or_create_state_machine(abp, "Locomotion")
    idle = load("%s/AC_Idle" % DIR)
    walk = load("%s/AC_Walk_Loop" % DIR)
    say("idle clip = %s, walk clip = %s" % (
        idle.get_name() if idle else None, walk.get_name() if walk else None))

    for state, clip in (("Idle", idle), ("Walk", walk), ("Run", walk)):
        if not clip:
            say("  %s skipped, no clip" % state)
            continue
        ok = unreal.NobleAnimGraphAuthoring.set_state_sequence(sm, state, clip, True)
        say("  %-5s -> %-14s %s" % (state, clip.get_name(), ok))

    say("")
    say("--- read back ---")
    for state in ("Idle", "Walk", "Run"):
        say("  %-5s -> %s" % (
            state, unreal.NobleAnimGraphAuthoring.get_state_sequence_name(sm, state)))
    say("compiled = %s" % unreal.NobleAnimGraphAuthoring.compile_anim_blueprint(abp))
    say("saved    = %s" % unreal.EditorAssetLibrary.save_asset(ABP, only_if_is_dirty=False))

    # --- 4. report frame counts ------------------------------------------
    say("")
    say("--- final clips ---")
    for path in unreal.EditorAssetLibrary.list_assets(DIR, recursive=False):
        clip = unreal.EditorAssetLibrary.load_asset(path)
        frames = unreal.AnimationLibrary.get_num_frames(clip) if clip else -1
        say("  %-28s %d frames" % (path.split("/")[-1].split(".")[0], frames))
except Exception as exc:
    say("FAILED: %s" % exc)

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
unreal.log("[NA-CONSOLIDATE] wrote %d lines" % len(lines))
