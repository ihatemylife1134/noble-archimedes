"""Import the downloaded character into the running Blender UI and frame it.

Deliberately minimal: no read_factory_settings (that reinitialises Blender during
startup and crashes the GUI), no file saving, no context overrides beyond a
guarded viewport frame.
"""
import os

import bpy
from mathutils import Vector

FBX = os.path.join(os.environ["USERPROFILE"], "Downloads", "survival_character.fbx")

# Clear the default cube/camera/light instead of reloading the file.
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

bpy.ops.import_scene.fbx(filepath=FBX)

meshes = [o for o in bpy.data.objects if o.type == "MESH"]
armatures = [o for o in bpy.data.objects if o.type == "ARMATURE"]
print("NA-BLENDER imported %d meshes, %d armatures" % (len(meshes), len(armatures)))

try:
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"

    xs, ys, zs = [], [], []
    for o in meshes:
        for corner in o.bound_box:
            v = o.matrix_world @ Vector(corner)
            xs.append(v.x)
            ys.append(v.y)
            zs.append(v.z)

    if xs:
        centre = Vector(((min(xs) + max(xs)) / 2,
                         (min(ys) + max(ys)) / 2,
                         (min(zs) + max(zs)) / 2))
        distance = (max(zs) - min(zs)) * 1.7
        for area in bpy.context.screen.areas:
            if area.type != "VIEW_3D":
                continue
            r3d = area.spaces.active.region_3d
            r3d.view_location = centre
            r3d.view_distance = distance
            r3d.view_perspective = "PERSP"
            break
        print("NA-BLENDER framed height=%.2f" % (max(zs) - min(zs)))
except Exception as exc:  # noqa: BLE001 - framing is cosmetic
    print("NA-BLENDER framing skipped: %s" % exc)
