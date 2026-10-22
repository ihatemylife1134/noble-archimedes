"""Trim an ActorCore FBX to its motion action, and VERIFY the result animates.

Each ActorCore FBX carries two actions: the motion, and a 900-frame "0_Open A_UE5"
reference pose. UE imports both into one 900-frame clip, so the motion occupies
the opening frames and the rest is a static hold -- the character animates and
then freezes.

The previous version of this script exported a file that reported the right
action and frame range but contained a *static* pose, which was only discovered
after it had been imported and the old clips deleted. So this version verifies its
own output: it re-imports the exported FBX into a cleared scene and samples bones
across the clip, reporting whether the motion actually survived.

Run headless:
    blender -b -P blender_trim_motion.py -- <in fbx> <out fbx>
"""
import os
import sys

import bpy

OUT = os.path.join(os.environ["TEMP"], "trim_motion.txt")
BONES = ("thigh_l", "upperarm_r", "hand_l")
lines = []


def say(m):
    lines.append(str(m))


def clear_scene():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for action in list(bpy.data.actions):
        bpy.data.actions.remove(action)


def sample_armature(armature, frames):
    """Return each bone's pose rotation at several frames."""
    samples = []
    for frame in frames:
        bpy.context.scene.frame_set(frame)
        bpy.context.view_layer.update()
        row = {}
        for bone in BONES:
            pose_bone = armature.pose.bones.get(bone)
            if pose_bone:
                q = pose_bone.matrix.to_quaternion()
                row[bone] = (round(q.x, 4), round(q.y, 4), round(q.z, 4), round(q.w, 4))
        samples.append((frame, row))
    return samples


def report_motion(label, samples):
    moved = {}
    for bone in BONES:
        values = [row.get(bone) for _, row in samples if bone in row]
        if len(values) > 1:
            moved[bone] = len(set(values)) > 1
    say("  %s: %s" % (label, ", ".join(
        "%s=%s" % (b, "MOVES" if v else "static") for b, v in moved.items()) or "no bones found"))
    return any(moved.values())



def main():
    argv = sys.argv
    if "--" not in argv or len(argv) < argv.index("--") + 3:
        say("usage: blender -b -P blender_trim_motion.py -- <in fbx> <out fbx>")
        return

    src = argv[argv.index("--") + 1]
    dst = argv[argv.index("--") + 2]
    say("in  = %s" % src)
    say("out = %s" % dst)

    clear_scene()
    bpy.ops.import_scene.fbx(filepath=src)

    armatures = [o for o in bpy.data.objects if o.type == "ARMATURE"]
    say("armatures = %d" % len(armatures))
    for arm in armatures:
        action = arm.animation_data.action if arm.animation_data else None
        say("  '%s' bones=%d action=%s nla=%d" % (
            arm.name, len(arm.data.bones),
            action.name if action else None,
            len(arm.animation_data.nla_tracks) if arm.animation_data else 0))

    say("actions:")
    for action in bpy.data.actions:
        span = action.frame_range
        say("  %-40s frames %.0f..%.0f" % (action.name, span[0], span[1]))

    motion = [a for a in bpy.data.actions if "0_Open" not in a.name and "UE5" not in a.name]
    if not motion:
        say("no motion action found")
        return
    keep = motion[0]
    span = keep.frame_range
    say("keeping '%s' frames %.0f..%.0f" % (keep.name, span[0], span[1]))

    # The action must be bound to the armature whose bones its curves address;
    # binding it to the wrong armature yields a static export.
    target = None
    for arm in armatures:
        if arm.animation_data and arm.animation_data.action == keep:
            target = arm
            break
    if target is None:
        target = next((a for a in armatures if a.animation_data),
                      armatures[0] if armatures else None)
    if target is None:
        say("no armature to bind to")
        return

    if not target.animation_data:
        target.animation_data_create()

    # Strip CC3+ helper bones that the target skeleton does not have. Their
    # animation curves make UE abort the import with "Unable to retrieve bone
    # index for track: cc_base_...", and walking animates the leg twist bones
    # where idling does not, so only some clips trip over this.
    stripped = []
    bpy.context.view_layer.objects.active = target
    try:
        bpy.ops.object.mode_set(mode="EDIT")
        for edit_bone in list(target.data.edit_bones):
            if edit_bone.name.startswith("cc_base_"):
                stripped.append(edit_bone.name)
                target.data.edit_bones.remove(edit_bone)
        bpy.ops.object.mode_set(mode="OBJECT")
        say("stripped %d cc_base_* bones" % len(stripped))
    except Exception as exc:  # noqa: BLE001
        say("bone strip failed: %s" % exc)
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:  # noqa: BLE001
            pass

    target.animation_data.action = keep

    # Blender 4.4+ stores animation per "action slot". Assigning the action alone
    # leaves it inert -- the armature keeps evaluating the previously bound
    # action, which is why binding the motion produced a static pose and the
    # export baked that pose. The slot has to be assigned as well.
    try:
        slots = list(getattr(keep, "slots", []))
        if slots:
            target.animation_data.action_slot = slots[0]
            say("assigned action slot '%s'" % getattr(slots[0], "name_display", slots[0].name))
        else:
            say("action exposes no slots (pre-4.4 behaviour)")
    except Exception as exc:  # noqa: BLE001
        say("could not assign action slot: %s" % exc)

    say("bound '%s' to armature '%s'" % (keep.name, target.name))

    # Drop the reference action so it cannot be exported alongside the motion.
    # Capture the name first: remove() invalidates the Action struct.
    for action in list(bpy.data.actions):
        if action != keep:
            name = action.name
            bpy.data.actions.remove(action)
            say("removed action '%s'" % name)

    scene = bpy.context.scene
    scene.frame_start = int(span[0])
    scene.frame_end = int(span[1])
    bpy.context.view_layer.update()

    say("")
    say("pre-export motion check:")
    report_motion("source", sample_armature(
        target, [int(span[0]), int((span[0] + span[1]) // 2), int(span[1])]))

    os.makedirs(os.path.dirname(dst), exist_ok=True)
    bpy.ops.export_scene.fbx(
        filepath=dst,
        use_selection=False,
        bake_anim=True,
        bake_anim_use_all_actions=False,
        bake_anim_use_nla_strips=False,
        bake_anim_force_startend_keying=True,
        bake_anim_simplify_factor=0.0,
        add_leaf_bones=False,
    )
    say("exported %.2f MB" % (os.path.getsize(dst) / 1048576.0))

    # Verify the exported file itself, rather than trusting the export.
    say("")
    say("post-export verification (re-importing the file just written):")
    clear_scene()
    bpy.ops.import_scene.fbx(filepath=dst)
    check = [o for o in bpy.data.objects if o.type == "ARMATURE"]
    if not check:
        say("  FAILED: exported file has no armature")
        return
    arm = check[0]
    action = arm.animation_data.action if arm.animation_data else None
    say("  re-imported armature '%s' action=%s" % (arm.name, action.name if action else None))
    if not action:
        say("  VERDICT: exported file has no action -- do not import this")
        return
    lo, hi = int(action.frame_range[0]), int(action.frame_range[1])
    samples = sample_armature(arm, [lo, lo + (hi - lo) // 4, lo + (hi - lo) // 2, hi])
    if report_motion("exported", samples):
        say("  VERDICT: the exported file animates")
    else:
        say("  VERDICT: THE EXPORTED FILE IS STATIC -- do not import this")


try:
    main()
except Exception as exc:  # noqa: BLE001
    say("FAILED: %s" % exc)

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
print("wrote %s" % OUT)
