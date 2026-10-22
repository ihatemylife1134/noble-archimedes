"""Inspect an ActorCore motion FBX: rig, bone naming and animation length.

ActorCore exports in "Unreal" format carry a full CC3+ character (mesh + rig)
plus the motion. What matters for integration is whether the bone naming can be
mapped onto the character's mannequin-derived skeleton, and how long the motion
is.

Run headless:
    blender -b -P blender_check_motion.py -- <fbx path>
"""
import os
import sys

import bpy

OUT = os.path.join(os.environ["TEMP"], "motion_fbx.txt")

# Bones the character shares with the UE mannequin, per the earlier bone
# compatibility check (45 shared, 0 new-only).
MANNEQUIN = [
    "root", "pelvis", "spine_01", "spine_02", "spine_03", "spine_04", "spine_05",
    "neck_01", "neck_02", "head",
    "clavicle_l", "clavicle_r", "upperarm_l", "upperarm_r",
    "lowerarm_l", "lowerarm_r", "hand_l", "hand_r",
    "thigh_l", "thigh_r", "calf_l", "calf_r", "foot_l", "foot_r",
    "ball_l", "ball_r",
]
lines = []


def say(m):
    lines.append(str(m))


def main():
    argv = sys.argv
    fbx = argv[argv.index("--") + 1] if "--" in argv else None
    if not fbx or not os.path.exists(fbx):
        say("no fbx supplied")
        return

    say("fbx = %s (%.1f MB)" % (os.path.basename(fbx), os.path.getsize(fbx) / 1048576))

    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.ops.import_scene.fbx(filepath=fbx)

    armatures = [o for o in bpy.data.objects if o.type == "ARMATURE"]
    meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    say("armatures = %d, meshes = %d" % (len(armatures), len(meshes)))

    for arm in armatures:
        bones = [b.name for b in arm.data.bones]
        say("")
        say("armature '%s': %d bones" % (arm.name, len(bones)))
        say("first 30: %s" % bones[:30])

        found = [b for b in MANNEQUIN if b in bones]
        missing = [b for b in MANNEQUIN if b not in bones]
        say("")
        say("mannequin-name matches: %d/%d" % (len(found), len(MANNEQUIN)))
        say("missing: %s" % missing)
        say("bones not in the mannequin list (sample): %s" % [b for b in bones if b not in MANNEQUIN][:25])

    say("")
    say("actions:")
    for action in bpy.data.actions:
        try:
            span = action.frame_range
            say("  %-40s frames %.0f..%.0f (%.2fs at 30fps)" % (
                action.name, span[0], span[1], (span[1] - span[0]) / 30.0))
        except Exception as exc:  # noqa: BLE001
            say("  %-40s frame range failed: %s" % (action.name, exc))


try:
    main()
except Exception as exc:  # noqa: BLE001
    say("FAILED: %s" % exc)

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
print("wrote %s" % OUT)
