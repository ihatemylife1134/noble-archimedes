"""Hector skeleton + procedural mesh. Private-use fan rebuild; all geometry generated."""
import bpy, bmesh, math
from mathutils import Vector

# name, parent, head, tail  (Blender: Z up, -Y forward, +X = character's left; cm)
BONES = [
    ("root", None, (0, 0, 0), (0, 0, 20)),
    ("pelvis", "root", (0, 0, 98), (0, 0, 108)),
    ("spine_01", "pelvis", (0, 0, 108), (0, 0, 122)),
    ("spine_02", "spine_01", (0, 0, 122), (0, 0, 138)),
    ("spine_03", "spine_02", (0, 0, 138), (0, 0, 150)),
    ("neck_01", "spine_03", (0, 0, 150), (0, 0, 158)),
    ("head", "neck_01", (0, 0, 158), (0, 0, 180)),
    ("clavicle_l", "spine_03", (3, 0, 146), (16, 0, 147)),
    ("upperarm_l", "clavicle_l", (16, 0, 147), (44, 0, 147)),
    ("lowerarm_l", "upperarm_l", (44, 0, 147), (70, 0, 147)),
    ("hand_l", "lowerarm_l", (70, 0, 147), (80, 0, 147)),
    ("clavicle_r", "spine_03", (-3, 0, 146), (-16, 0, 147)),
    ("upperarm_r", "clavicle_r", (-16, 0, 147), (-44, 0, 147)),
    ("lowerarm_r", "upperarm_r", (-44, 0, 147), (-70, 0, 147)),
    ("hand_r", "lowerarm_r", (-70, 0, 147), (-80, 0, 147)),
    ("weapon_r", "hand_r", (-77, -2, 147), (-77, -2, 160)),
    ("thigh_l", "pelvis", (10, 0, 98), (10, 0, 54)),
    ("calf_l", "thigh_l", (10, 0, 54), (10, 2, 10)),
    ("foot_l", "calf_l", (10, 2, 10), (10, -14, 2)),
    ("thigh_r", "pelvis", (-10, 0, 98), (-10, 0, 54)),
    ("calf_r", "thigh_r", (-10, 0, 54), (-10, 2, 10)),
    ("foot_r", "calf_r", (-10, 2, 10), (-10, -14, 2)),
]
BONE_INDEX = {b[0]: i for i, b in enumerate(BONES)}

MAT_DEFS = [  # name, rgb, roughness, metallic
    ("Skin", (0.80, 0.62, 0.52), 0.55, 0.0),
    ("Hair", (0.82, 0.84, 0.88), 0.45, 0.0),
    ("Coat", (0.05, 0.05, 0.07), 0.60, 0.0),
    ("Trim", (0.55, 0.08, 0.10), 0.50, 0.0),
    ("Leather", (0.18, 0.11, 0.07), 0.65, 0.0),
    ("Metal", (0.62, 0.62, 0.66), 0.30, 1.0),
    ("Gold", (0.83, 0.62, 0.22), 0.30, 1.0),
]
MAT_ORDER = [m[0] for m in MAT_DEFS]


def build_armature(scene):
    data = bpy.data.armatures.new("Hector_Skeleton")
    obj = bpy.data.objects.new("Armature", data)
    scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    for name, parent, h, t in BONES:
        b = data.edit_bones.new(name)
        b.head, b.tail, b.roll = Vector(h), Vector(t), 0.0
        if parent:
            b.parent = data.edit_bones[parent]
    bpy.ops.object.mode_set(mode='OBJECT')
    return obj


def _tube(p0, p1, r0, r1, seg=10, rings=4, squash=(1.0, 1.0)):
    p0, p1 = Vector(p0), Vector(p1)
    axis = p1 - p0
    z = axis.normalized()
    ref = Vector((0, 0, 1)) if abs(z.z) < 0.95 else Vector((1, 0, 0))
    x = z.cross(ref).normalized()
    y = z.cross(x).normalized()
    vs, fs = [], []
    for r in range(rings + 1):
        t = r / rings
        rad, c = r0 + (r1 - r0) * t, p0 + axis * t
        for s in range(seg):
            a = 2 * math.pi * s / seg
            vs.append(c + x * math.cos(a) * rad * squash[0] + y * math.sin(a) * rad * squash[1])
    for r in range(rings):
        for s in range(seg):
            a, b = r * seg + s, r * seg + (s + 1) % seg
            fs.append((a, b, b + seg, a + seg))
    i0 = len(vs); vs.append(p0)
    i1 = len(vs); vs.append(p1)
    for s in range(seg):
        fs.append((i0, (s + 1) % seg, s))
        fs.append((i1, rings * seg + s, rings * seg + (s + 1) % seg))
    return vs, fs


def _ellipsoid(c, r, seg=14, rings=10):
    c = Vector(c)
    vs = [c + Vector((0, 0, -r[2]))]
    for i in range(1, rings):
        phi = math.pi * i / rings - math.pi / 2
        for s in range(seg):
            th = 2 * math.pi * s / seg
            vs.append(c + Vector((math.cos(phi) * math.cos(th) * r[0],
                                  math.cos(phi) * math.sin(th) * r[1], math.sin(phi) * r[2])))
    top = len(vs); vs.append(c + Vector((0, 0, r[2])))
    fs = [(0, 1 + (s + 1) % seg, 1 + s) for s in range(seg)]
    for i in range(rings - 2):
        for s in range(seg):
            a, b = 1 + i * seg + s, 1 + i * seg + (s + 1) % seg
            fs.append((a, b, b + seg, a + seg))
    base = 1 + (rings - 2) * seg
    fs += [(base + s, base + (s + 1) % seg, top) for s in range(seg)]
    return vs, fs


def _box(c, size):
    c, s = Vector(c), Vector(size) / 2
    vs = [c + Vector((a * s.x, b * s.y, d * s.z)) for a in (-1, 1) for b in (-1, 1) for d in (-1, 1)]
    return vs, [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]



def _one(b):
    return lambda co: {b: 1.0}


def _blend_z(lo, hi, z0, z1):
    def f(co):
        t = min(max((co.z - z0) / (z1 - z0), 0.0), 1.0)
        return {lo: 1 - t, hi: t}
    return f


def _blend_x(inner, outer, x0, x1):
    def f(co):
        t = min(max((abs(co.x) - x0) / (x1 - x0), 0.0), 1.0)
        return {inner: 1 - t, outer: t}
    return f


def build_mesh(scene, arm_obj):
    bm = bmesh.new()
    deform = bm.verts.layers.deform.verify()

    def part(geo, mat, weights):
        vs, fs = geo
        nv = [bm.verts.new(v) for v in vs]
        for v in nv:
            for bn, w in weights(v.co).items():
                if w > 0.001:
                    v[deform][BONE_INDEX[bn]] = w
        for f in fs:
            try:
                face = bm.faces.new([nv[i] for i in f])
                face.material_index = MAT_ORDER.index(mat)
                face.smooth = True
            except ValueError:
                pass

    T, E, B = _tube, _ellipsoid, _box
    for side, sx in (("l", 1), ("r", -1)):
        th, ca, ft = f"thigh_{side}", f"calf_{side}", f"foot_{side}"
        cl, ua, la, ha = f"clavicle_{side}", f"upperarm_{side}", f"lowerarm_{side}", f"hand_{side}"
        part(T((10*sx, 0, 98), (10*sx, 0, 56), 8.5, 6.5, rings=5), "Leather", _blend_z(th, "pelvis", 90, 100))
        part(T((10*sx, 0, 58), (10*sx, 1, 26), 6.2, 5.2), "Leather", _blend_z(ca, th, 50, 60))
        part(T((10*sx, 1, 30), (10*sx, 2, 6), 6.4, 6.0, rings=3), "Coat", _one(ca))          # boot shaft
        part(B((10*sx, -5, 4), (11, 22, 8)), "Coat", _one(ft))                               # boot foot
        part(B((10*sx, 1, 30), (13.4, 13.4, 2.5)), "Gold", _one(ca))                         # boot cuff
        part(T((14*sx, 0, 147), (44*sx, 0, 146), 6.5, 5.5), "Coat", _blend_x(cl, ua, 12, 20))
        part(T((43*sx, 0, 146), (64*sx, 0, 146), 5.4, 4.6), "Coat", _blend_x(ua, la, 40, 48))
        part(T((58*sx, 0, 146), (70*sx, 0, 146), 5.4, 5.0, rings=2), "Metal", _one(la))      # gauntlet
        part(T((70*sx, 0, 146), (79*sx, -1, 146), 3.6, 3.2, rings=2, squash=(1, 0.7)), "Leather", _one(ha))
        part(E((19*sx, 0, 149), (8, 8, 5)), "Metal", _one(cl))                               # pauldron
        part(B((8*sx, -6, 76), (15, 2, 40)), "Coat", _blend_z(th, "pelvis", 80, 96))         # coat tail front
        part(B((8*sx, 7, 70), (16, 2, 52)), "Coat", _blend_z(th, "pelvis", 80, 96))          # coat tail back
        part(B((8*sx, -7.2, 57), (15.2, 0.6, 2)), "Trim", _one(th))
        part(B((3.4*sx, -10.4, 168), (2.4, 0.6, 1.1)), "Metal", _one("head"))                # eyes
    part(T((0, 0, 96), (0, 0, 150), 16, 18, rings=6, squash=(1, 0.62)), "Coat", _blend_z("pelvis", "spine_03", 100, 145))
    part(T((0, 0, 104), (0, 0, 110), 16.8, 16.8, rings=1, squash=(1, 0.66)), "Trim", _one("pelvis"))   # sash
    part(B((0, -11.5, 128), (6, 1.5, 34)), "Gold", _one("spine_02"))                                    # clasps
    part(T((0, 0, 148), (0, 0, 158), 9.5, 8.0, rings=2), "Trim", _one("neck_01"))                       # collar
    part(T((0, 0, 150), (0, 0, 160), 5, 5, rings=1), "Skin", _one("neck_01"))
    part(E((0, -1, 168), (9, 10, 12)), "Skin", _one("head"))
    part(E((0, 2, 172), (10, 10.5, 11)), "Hair", _one("head"))
    part(T((0, 6, 170), (0, 12, 140), 8.5, 3.0, squash=(1, 0.5)), "Hair", _blend_z("spine_03", "head", 145, 162))

    mesh = bpy.data.meshes.new("SK_Hector")
    bm.to_mesh(mesh)
    bm.free()
    for name, rgb, rough, metal in MAT_DEFS:
        m = bpy.data.materials.new(f"M_Hector_{name}")
        m.use_nodes = True
        bsdf = m.node_tree.nodes["Principled BSDF"]
        bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
        bsdf.inputs["Roughness"].default_value = rough
        bsdf.inputs["Metallic"].default_value = metal
        mesh.materials.append(m)
    obj = bpy.data.objects.new("SK_Hector", mesh)
    scene.collection.objects.link(obj)
    for name, *_ in BONES:
        obj.vertex_groups.new(name=name)
    obj.parent = arm_obj
    obj.modifiers.new("Armature", 'ARMATURE').object = arm_obj
    return obj
