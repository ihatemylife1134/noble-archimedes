"""Compare bone motion between an ActorCore-imported clip and a retargeted one.

The retargeted clips are static (verified: every frame holds the same pose, and
Idle and Walk share identical values). These ActorCore FBXs were imported
straight onto the character's skeleton instead, so they should carry real motion.

Two earlier versions of this probe gave false answers -- comparing repr() (which
embeds the memory address) and comparing two identical error strings -- so this
compares numeric transform components and reports sampling failures as failures.
"""
import os

import unreal

OUT = os.path.join(os.environ["TEMP"], "clip_moves3.txt")
CLIPS = [
    "/Game/Characters/HectorBase/ActorCore/AC_Idlemale-idle_279398",
    "/Game/Characters/HectorBase/ActorCore/AC_Walk_Loopwalk-relaxed-2loop-378986",
    "/Game/Characters/HectorBase/ActorCore/AC_Walk_Startwalk-relaxed-1start-379003",
    "/Game/Characters/HectorBase/Retargeted/RTG_anim_Idle",
]
BONES = ["thigh_l", "upperarm_r", "hand_l"]
lines = []


def say(m):
    lines.append(str(m))


def sample(clip, bone, frame):
    """Bone pose at a frame; get_bone_pose_for_frame needs extract_root_motion."""
    fn = getattr(unreal.AnimationLibrary, "get_bone_pose_for_frame", None)
    if not fn:
        return "no sampler"
    try:
        return fn(clip, bone, frame, False)
    except Exception as exc:  # noqa: BLE001
        return "err: %s" % exc


def numeric(transform):
    try:
        t = transform.translation
        r = transform.rotation
        return (round(t.x, 3), round(t.y, 3), round(t.z, 3),
                round(r.x, 4), round(r.y, 4), round(r.z, 4), round(r.w, 4))
    except AttributeError:
        return None


try:
    for path in CLIPS:
        clip = unreal.EditorAssetLibrary.load_asset(path)
        name = path.split("/")[-1]
        if not clip:
            say("=== %-46s MISSING" % name)
            continue
        frames = unreal.AnimationLibrary.get_num_frames(clip)
        say("=== %s  (%d frames)" % (name, frames))
        for bone in BONES:
            a = sample(clip, bone, 0)
            b = sample(clip, bone, max(1, frames // 2))
            na, nb = numeric(a), numeric(b)
            if na is None or nb is None:
                say("   %-11s could not sample: %s" % (bone, a))
                continue
            say("   %-11s f0  =%s" % (bone, na))
            say("   %-11s f%-3d=%s" % ("", frames // 2, nb))
            say("   %-11s -> %s" % ("", "STATIC" if na == nb else "MOVES"))
        say("")
except Exception as exc:
    say("FAILED: %s" % exc)

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
unreal.log("[NA-CLIPMOVES3] wrote %d lines" % len(lines))
