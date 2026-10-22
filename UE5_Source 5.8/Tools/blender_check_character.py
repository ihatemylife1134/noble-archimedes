"""Report the character FBX's dimensions, orientation and bone names."""
import os

import bpy

FBX = os.path.join(os.environ["USERPROFILE"], "Downloads", "survival_character.fbx")
OUT = r"C:\Users\Madi\AppData\Local\Temp\blender_char.txt"
lines = []

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=FBX)

meshes = [o for o in bpy.data.objects if o.type == "MESH"]
armatures = [o for o in bpy.data.objects if o.type == "ARMATURE"]

lines.append("meshes=%d armatures=%d" % (len(meshes), len(armatures)))
for o in meshes[:6]:
    lines.append("  mesh %-22s dims=(%.1f, %.1f, %.1f) loc=(%.1f, %.1f, %.1f) scale=(%.2f, %.2f, %.2f)"
                 % (o.name, o.dimensions.x, o.dimensions.y, o.dimensions.z,
                    o.location.x, o.location.y, o.location.z,
                    o.scale.x, o.scale.y, o.scale.z))

xs, ys, zs = [], [], []
from mathutils import Vector
for o in meshes:
    for corner in o.bound_box:
        v = o.matrix_world @ Vector(corner)
        xs.append(v.x)
        ys.append(v.y)
        zs.append(v.z)

if xs:
    lines.append("bbox X %.1f..%.1f (%.1f)  Y %.1f..%.1f (%.1f)  Z %.1f..%.1f (%.1f)"
                 % (min(xs), max(xs), max(xs) - min(xs),
                    min(ys), max(ys), max(ys) - min(ys),
                    min(zs), max(zs), max(zs) - min(zs)))
    lines.append("height(Z)=%.1f units  width(X)=%.1f  depth(Y)=%.1f"
                 % (max(zs) - min(zs), max(xs) - min(xs), max(ys) - min(ys)))

for arm in armatures:
    lines.append("armature %s bones=%d" % (arm.name, len(arm.data.bones)))
    lines.append("  " + ", ".join(b.name for b in list(arm.data.bones)[:14]))
    axes = [b.name for b in arm.data.bones if b.name.lower() in
            ("pelvis", "root", "head", "foot_l", "spine_01")]
    lines.append("  key bones present: %s" % axes)

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
print("\n".join(lines))
