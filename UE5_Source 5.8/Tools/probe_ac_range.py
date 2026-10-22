"""Find where the motion actually sits inside each ActorCore clip.

The imported clips all report 900 frames, which is the length of the FBX's
"0_Open A_UE5" reference-pose action. If the real motion only occupies part of
that range, playing the clip as-is would animate briefly and then hold still, so
the active range has to be measured before anything is wired up.

Samples one bone across the whole clip and reports where it changes.
"""
import os

import unreal

OUT = os.path.join(os.environ["TEMP"], "ac_range.txt")
CLIPS = [
    "/Game/Characters/HectorBase/ActorCore/AC_Idle",
    "/Game/Characters/HectorBase/ActorCore/AC_Walk_Loop",
    "/Game/Characters/HectorBase/ActorCore/AC_Idle",
    "/Game/Characters/HectorBase/ActorCore/AC_Idle",
]
BONE = "thigh_l"
STEPS = 20
lines = []


def say(m):
    lines.append(str(m))


def rot_at(clip, frame):
    fn = getattr(unreal.AnimationLibrary, "get_bone_pose_for_frame", None)
    if not fn:
        return None
    try:
        pose = fn(clip, BONE, frame, False)
        r = pose.rotation
        return (round(r.x, 5), round(r.y, 5), round(r.z, 5), round(r.w, 5))
    except Exception as exc:  # noqa: BLE001
        return "err: %s" % exc


try:
    for path in CLIPS:
        clip = unreal.EditorAssetLibrary.load_asset(path)
        name = path.split("/")[-1]
        if not clip:
            say("%-46s MISSING" % name)
            continue
        frames = unreal.AnimationLibrary.get_num_frames(clip)
        say("=== %s  (%d frames)" % (name, frames))

        samples = []
        for i in range(STEPS + 1):
            frame = int(round(frames * i / STEPS))
            samples.append((frame, rot_at(clip, frame)))

        previous = None
        for frame, value in samples:
            changed = ""
            if previous is not None and isinstance(value, tuple) and isinstance(previous, tuple):
                delta = max(abs(a - b) for a, b in zip(value, previous))
                changed = "changed" if delta > 0.001 else ""
            say("   f%-5d %s %s" % (frame, value, changed))
            previous = value

        moving = [f for (f, v), (pf, pv) in zip(samples[1:], samples[:-1])
                  if isinstance(v, tuple) and isinstance(pv, tuple)
                  and max(abs(a - b) for a, b in zip(v, pv)) > 0.001]
        if moving:
            say("   -> motion between frames %d and %d" % (min(moving), max(moving)))
        else:
            say("   -> NO motion detected anywhere in the clip")
        say("")
except Exception as exc:
    say("FAILED: %s" % exc)

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
unreal.log("[NA-ACRANGE] wrote %d lines" % len(lines))
