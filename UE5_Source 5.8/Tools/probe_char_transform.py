"""Resolve the new character's facing sign by accumulating the bone chain.

AnimPose.get_bone_pose returns PARENT-RELATIVE transforms, so the earlier
measurement was meaningless. Compose the chain from the root down to foot_l and
ball_l to get their mesh-space positions; the ball of the foot is ahead of the
ankle, so foot_l -> ball_l is the mesh's forward axis.
"""
import unreal

OUT = r"C:\Users\Madi\AppData\Local\Temp\probe_char6.txt"
MESH = "/Game/Characters/HectorBase/SK_HectorBase"
CHAR_BP = "/Game/Blueprints/Characters/BP_HectorCharacter"
lines = []


def say(m):
    lines.append(str(m))


def qrot(q, v):
    """Rotate vector v by quaternion q=(x,y,z,w) without engine helpers."""
    x, y, z, w = q.x, q.y, q.z, q.w
    tx = 2.0 * (y * v.z - z * v.y)
    ty = 2.0 * (z * v.x - x * v.z)
    tz = 2.0 * (x * v.y - y * v.x)
    return unreal.Vector(
        v.x + w * tx + (y * tz - z * ty),
        v.y + w * ty + (z * tx - x * tz),
        v.z + w * tz + (x * ty - y * tx))


def qmul(a, b):
    ax, ay, az, aw = a.x, a.y, a.z, a.w
    bx, by, bz, bw = b.x, b.y, b.z, b.w
    return unreal.Quat(
        aw * bx + ax * bw + ay * bz - az * by,
        aw * by - ax * bz + ay * bw + az * bx,
        aw * bz + ax * by - ay * bx + az * bw,
        aw * bw - ax * bx - ay * by - az * bz)


try:
    mesh = unreal.EditorAssetLibrary.load_asset(MESH)
    skel = mesh.get_editor_property("skeleton")
    pose = skel.get_reference_pose()

    # parent map
    parents = {}
    for name in pose.get_bone_names():
        p = mesh.get_bone_parent(name)
        parents[str(name)] = str(p) if p else None
    say("bones = %d" % len(parents))

    cache = {}

    def mesh_space(bone, depth=0):
        if bone in cache:
            return cache[bone]
        if depth > 300:
            return None
        local = pose.get_bone_pose(bone)
        parent = parents.get(bone)
        if not parent:
            result = (local.translation, local.rotation)
        else:
            up = mesh_space(parent, depth + 1)
            if up is None:
                return None
            pt, pr = up
            result = (pt + qrot(pr, local.translation), qmul(pr, local.rotation))
        cache[bone] = result
        return result

    for bone in ("root", "pelvis", "foot_l", "ball_l", "foot_r", "ball_r", "head"):
        if bone not in parents:
            say("%-8s absent" % bone)
            continue
        ms = mesh_space(bone)
        if ms:
            say("%-8s mesh space = (%.2f, %.2f, %.2f)" % (bone, ms[0].x, ms[0].y, ms[0].z))

    foot = mesh_space("foot_l")
    ball = mesh_space("ball_l")
    if foot and ball:
        fwd = unreal.Vector(ball[0].x - foot[0].x, ball[0].y - foot[0].y, 0.0)
        if fwd.size() > 0.01:
            fwd = fwd.normalized()
            import math
            yaw = -math.degrees(math.atan2(fwd.y, fwd.x))
            say("mesh forward = (%.3f, %.3f, %.3f)" % (fwd.x, fwd.y, fwd.z))
            say("yaw correction to face +X = %.1f" % yaw)

            bp = unreal.EditorAssetLibrary.load_asset(CHAR_BP)
            cdo = unreal.get_default_object(bp.generated_class())
            comp = cdo.get_editor_property("mesh")
            say("mesh rot before = %s" % comp.get_editor_property("relative_rotation"))
            comp.set_editor_property("relative_rotation",
                                     unreal.Rotator(0.0, 0.0, yaw))
            say("mesh rot after  = %s" % comp.get_editor_property("relative_rotation"))
            unreal.EditorAssetLibrary.save_asset(
                CHAR_BP.split(".")[0], only_if_is_dirty=False)
            say("saved")
except Exception as exc:
    say("FAILED: %s" % exc)

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
unreal.log("[NA-PROBECHAR6] wrote %d lines" % len(lines))
