#!/usr/bin/env python3
"""Report what material Hector actually wears and whether the armor asset exists."""
import unreal

OUT = r"C:\Users\Madi\AppData\Local\Temp\diag_hector_mat.txt"
lines = []


def say(msg):
    lines.append(str(msg))


def get_prop(obj, name, default=None):
    import re
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    snake = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
    for candidate in (snake, name):
        try:
            return obj.get_editor_property(candidate)
        except Exception:
            continue
    return default


# 1. Does the material asset exist where the art pass expects it?
for path in ("/Game/Art/Materials/Armor",
             "/Game/Art/Materials/Generated/MI_Armor",
             "/Game/Art/Materials/Bone",
             "/Game/Art/Materials/Flesh"):
    exists = unreal.EditorAssetLibrary.does_asset_exist(path)
    mat = unreal.EditorAssetLibrary.load_asset(path) if exists else None
    say("asset %-38s exists=%s class=%s skeletal=%s"
        % (path, exists,
           mat.get_class().get_name() if mat else "-",
           (get_prop(mat, "used_with_skeletal_mesh") if mat else "-")))

# 2. What is the skeletal mesh asset itself pointing at?
mesh = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Hector/SK_Hector")
if mesh:
    mats = get_prop(mesh, "Materials")
    for index, slot in enumerate(mats or []):
        info = get_prop(slot, "material_interface")
        say("SK_Hector slot %d -> %s" % (index, info.get_path_name() if info else "None"))
else:
    say("SK_Hector not found")

# 3. What does BP_HectorCharacter override it with?
bp = unreal.EditorAssetLibrary.load_asset("/Game/Blueprints/Characters/BP_HectorCharacter")
if bp:
    cdo = unreal.get_default_object(bp.generated_class())
    comp = get_prop(cdo, "Mesh")
    overrides = get_prop(comp, "OverrideMaterials") if comp else None
    say("BP override count=%s" % (len(overrides) if overrides else 0))
    for index, mat in enumerate(overrides or []):
        say("BP override %d -> %s" % (index, mat.get_path_name() if mat else "None"))
else:
    say("BP_HectorCharacter not found")

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
unreal.log_warning("[DIAGMAT] written")
