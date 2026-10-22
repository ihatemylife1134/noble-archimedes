"""Import the trimmed ActorCore clips, verify they move, and rewire the states.

The clips were trimmed in Blender with the action slot assigned, and the exported
FBXs were verified to animate by re-importing them there. This does the same check
again after the UE import, sampling FIVE points across each clip: sampling only
start and midpoint lets a walk cycle return to the same phase and read as static,
which is how an earlier round of this work went wrong.

FBXIT_Animation is required on the import options; without it the task produces
no asset at all.
"""
import os

import unreal

OUT = r"C:\Users\Madi\AppData\Local\Temp\import_trimmed_final.txt"
DIR = "/Game/Characters/HectorBase/ActorCore"
ABP = "/Game/Characters/HectorBase/AB_HectorBaseV2"
SKELETON = "/Game/Characters/HectorBase/survival_character_Skeleton"
TRIMMED = r"C:\Projects\NobleArchimedes\ArtSource\ActorCore\Trimmed"
IMPORTS = [("AC_Idle.fbx", "AC_Idle"), ("AC_Walk_Loop.fbx", "AC_Walk_Loop")]
BONES = ["thigh_l", "upperarm_r"]
lines = []


def say(m):
    lines.append(str(m))


def load(path):
    return unreal.EditorAssetLibrary.load_asset(path) if \
        unreal.EditorAssetLibrary.does_asset_exist(path) else None


def pose_at(clip, bone, frame):
    fn = getattr(unreal.AnimationLibrary, "get_bone_pose_for_frame", None)
    if not fn:
        return None
    try:
        pose = fn(clip, bone, frame, False)
        t, r = pose.translation, pose.rotation
        return (round(t.x, 2), round(t.y, 2), round(t.z, 2),
                round(r.x, 4), round(r.y, 4), round(r.z, 4), round(r.w, 4))
    except Exception as exc:  # noqa: BLE001
        return "err: %s" % exc


def verify(clip):
    """Report whether the clip moves, sampling five points across it."""
    frames = unreal.AnimationLibrary.get_num_frames(clip)
    points = [int(frames * i / 4) for i in range(5)]
    verdict = {}
    for bone in BONES:
        values = [pose_at(clip, bone, f) for f in points]
        distinct = len({v for v in values if isinstance(v, tuple)})
        verdict[bone] = "MOVES" if distinct > 1 else "STATIC"
        say("    %-11s %s" % (bone, verdict[bone]))
        if verdict[bone] == "STATIC":
            say("      sampled: %s" % (values[:2],))
    return frames, all(v == "MOVES" for v in verdict.values())


def import_clip(fbx, name):
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
    options.set_editor_property("import_materials", False)
    options.set_editor_property("import_textures", False)
    options.set_editor_property("skeleton", load(SKELETON))
    options.set_editor_property("mesh_type_to_import",
                                unreal.FBXImportType.FBXIT_ANIMATION)
    task.set_editor_property("options", options)

    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    return load("%s/%s" % (DIR, name))


try:
    good = {}
    for fbx_name, asset_name in IMPORTS:
        full = os.path.join(TRIMMED, fbx_name)
        say("=== %s" % asset_name)
        if not os.path.exists(full):
            say("  MISSING on disk")
            continue
        clip = import_clip(full, asset_name)
        if not clip:
            say("  import produced no asset")
            continue
        frames, moves = verify(clip)
        say("  %d frames, animates = %s" % (frames, moves))
        if moves:
            good[asset_name] = clip
        say("")

    unreal.EditorAssetLibrary.save_directory(DIR, only_if_is_dirty=False, recursive=True)

    say("=== rewiring ===")
    abp = load(ABP)
    sm = unreal.NobleAnimGraphAuthoring.get_or_create_state_machine(abp, "Locomotion")
    for state, key in (("Idle", "AC_Idle"), ("Walk", "AC_Walk_Loop"), ("Run", "AC_Walk_Loop")):
        clip = good.get(key)
        if not clip:
            say("  %-5s SKIPPED - %s did not verify as animating" % (state, key))
            continue
        say("  %-5s -> %-14s %s" % (
            state, key,
            unreal.NobleAnimGraphAuthoring.set_state_sequence(sm, state, clip, True)))

    say("")
    for state in ("Idle", "Walk", "Run"):
        say("  %-5s -> %s" % (
            state, unreal.NobleAnimGraphAuthoring.get_state_sequence_name(sm, state)))
    say("compiled = %s" % unreal.NobleAnimGraphAuthoring.compile_anim_blueprint(abp))
    say("saved    = %s" % unreal.EditorAssetLibrary.save_asset(ABP, only_if_is_dirty=False))
except Exception as exc:
    say("FAILED: %s" % exc)

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
unreal.log("[NA-IMPORTTRIMMED] wrote %d lines" % len(lines))
