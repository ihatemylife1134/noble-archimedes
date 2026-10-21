#!/usr/bin/env python3
r"""Import original generated textures and build the Noble Archimedes material kit.

Prerequisite: run `generate_original_textures.py` first. This script reads a
staging directory outside the repository and imports the textures into the
active UE project. It does not read the local reference pack.

Run with:
    UnrealEditor-Cmd.exe <project>.uproject -run=PythonScript \
        -script="C:\Projects\NobleArchimedes\Tools\ue5_import_generated_textures.py" \
        -unattended -nosplash -nop4
"""
import os

import unreal

SOURCE = r"C:\Projects\NobleArchimedes\ArtSource\GeneratedTextures"
TEX_ROOT = "/Game/Art/Generated"
MAT_DIR = "/Game/Art/Materials/Generated"
MASTER_NAME = "M_NA_Surface_Master"
MASTER_PATH = "%s/%s" % (MAT_DIR, MASTER_NAME)
REBUILD = True

ASSET_TOOLS = unreal.AssetToolsHelpers.get_asset_tools()
EAL = unreal.EditorAssetLibrary
MEL = unreal.MaterialEditingLibrary


def say(msg):
    unreal.log_warning("[NA-TEXIMPORT] " + str(msg))


def families():
    if not os.path.isdir(SOURCE):
        return []
    result = []
    for name in sorted(os.listdir(SOURCE)):
        folder = os.path.join(SOURCE, name)
        if os.path.isdir(folder):
            result.append(name)
    return result


def import_texture(png_path, dest_path, dest_name, srgb, compression):
    task = unreal.AssetImportTask()
    task.set_editor_property("filename", png_path)
    task.set_editor_property("destination_path", dest_path)
    task.set_editor_property("destination_name", dest_name)
    task.set_editor_property("replace_existing", True)
    task.set_editor_property("automated", True)
    task.set_editor_property("save", False)
    task.set_editor_property("factory", unreal.TextureFactory())
    ASSET_TOOLS.import_asset_tasks([task])
    asset_path = "%s/%s" % (dest_path, dest_name)
    tex = EAL.load_asset(asset_path)
    if not tex:
        say("FAILED to import %s" % asset_path)
        return None
    try:
        tex.set_editor_property("srgb", srgb)
        tex.set_editor_property("compression_settings", compression)
        tex.set_editor_property("mip_gen_settings",
                                unreal.TextureMipGenSettings.TMGS_FROM_TEXTURE_GROUP)
        tex.set_editor_property("lod_group", unreal.TextureGroup.TEXTUREGROUP_WORLD)
        tex.set_editor_property("never_stream", False)
    except Exception as exc:
        say("texture settings warning for %s: %r" % (dest_name, exc))
    EAL.save_asset(asset_path, only_if_is_dirty=False)
    return tex


def delete_asset(path):
    if EAL.does_asset_exist(path):
        EAL.delete_asset(path)


def scalar_param(mat, name, default, x, y):
    expr = MEL.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, x, y)
    expr.set_editor_property("parameter_name", name)
    expr.set_editor_property("default_value", float(default))
    return expr


def vector_param(mat, name, rgb, x, y):
    expr = MEL.create_material_expression(mat, unreal.MaterialExpressionVectorParameter, x, y)
    expr.set_editor_property("parameter_name", name)
    expr.set_editor_property("default_value", unreal.LinearColor(rgb[0], rgb[1], rgb[2], 1.0))
    return expr


def build_master():
    delete_asset(MASTER_PATH)
    EAL.make_directory(MAT_DIR)
    mat = ASSET_TOOLS.create_asset(MASTER_NAME, MAT_DIR, unreal.Material,
                                   unreal.MaterialFactoryNew())
    if not mat:
        say("could not create master material")
        return None

    # Shared UV tiling.
    uv = MEL.create_material_expression(mat, unreal.MaterialExpressionTextureCoordinate, -1500, -300)
    tiling = scalar_param(mat, "UVTiling", 1.0, -1500, -200)
    uv_mul = MEL.create_material_expression(mat, unreal.MaterialExpressionMultiply, -1300, -300)
    MEL.connect_material_expressions(uv, "", uv_mul, "A")
    MEL.connect_material_expressions(tiling, "", uv_mul, "B")

    # Base color.
    base = MEL.create_material_expression(mat, unreal.MaterialExpressionTextureSampleParameter2D,
                                          -1100, -420)
    base.set_editor_property("parameter_name", "BaseColorTex")
    base.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_COLOR)
    MEL.connect_material_expressions(uv_mul, "", base, "UVs")
    tint = vector_param(mat, "BaseColorTint", (1.0, 1.0, 1.0), -1100, -260)
    base_mul = MEL.create_material_expression(mat, unreal.MaterialExpressionMultiply, -850, -360)
    MEL.connect_material_expressions(base, "RGB", base_mul, "A")
    MEL.connect_material_expressions(tint, "", base_mul, "B")
    MEL.connect_material_property(base_mul, "", unreal.MaterialProperty.MP_BASE_COLOR)

    # Normal.
    normal = MEL.create_material_expression(mat, unreal.MaterialExpressionTextureSampleParameter2D,
                                            -1100, -80)
    normal.set_editor_property("parameter_name", "NormalTex")
    normal.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
    MEL.connect_material_expressions(uv_mul, "", normal, "UVs")
    MEL.connect_material_property(normal, "RGB", unreal.MaterialProperty.MP_NORMAL)

    # ORM: R = AO, G = roughness, B = metallic.
    orm = MEL.create_material_expression(mat, unreal.MaterialExpressionTextureSampleParameter2D,
                                         -1100, 160)
    orm.set_editor_property("parameter_name", "ORMTex")
    # Linear color keeps the packed ORM channels in linear space while avoiding
    # the material compiler's default-mask sampler warning.
    orm.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR)
    MEL.connect_material_expressions(uv_mul, "", orm, "UVs")

    def mask(channel, y):
        node = MEL.create_material_expression(mat, unreal.MaterialExpressionComponentMask,
                                              -850, y)
        node.set_editor_property("r", channel == "r")
        node.set_editor_property("g", channel == "g")
        node.set_editor_property("b", channel == "b")
        node.set_editor_property("a", channel == "a")
        MEL.connect_material_expressions(orm, "RGB", node, "")
        return node

    MEL.connect_material_property(mask("r", 120), "", unreal.MaterialProperty.MP_AMBIENT_OCCLUSION)
    MEL.connect_material_property(mask("g", 220), "", unreal.MaterialProperty.MP_ROUGHNESS)
    MEL.connect_material_property(mask("b", 320), "", unreal.MaterialProperty.MP_METALLIC)

    # Emissive.
    emissive = MEL.create_material_expression(mat, unreal.MaterialExpressionTextureSampleParameter2D,
                                              -1100, 440)
    emissive.set_editor_property("parameter_name", "EmissiveTex")
    emissive.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_COLOR)
    MEL.connect_material_expressions(uv_mul, "", emissive, "UVs")
    strength = scalar_param(mat, "EmissiveStrength", 1.0, -1100, 600)
    emul = MEL.create_material_expression(mat, unreal.MaterialExpressionMultiply, -850, 480)
    MEL.connect_material_expressions(emissive, "RGB", emul, "A")
    MEL.connect_material_expressions(strength, "", emul, "B")
    MEL.connect_material_property(emul, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)

    MEL.recompile_material(mat)
    EAL.save_asset(MASTER_PATH, only_if_is_dirty=False)
    say("master material ready: %s" % MASTER_PATH)
    return mat


def build_instance(master, family, textures, name=None, tint=None, tiling=1.0,
                   emissive=0.0):
    name = name or ("MI_%s" % family)
    path = "%s/%s" % (MAT_DIR, name)
    delete_asset(path)
    factory = unreal.MaterialInstanceConstantFactoryNew()
    mi = ASSET_TOOLS.create_asset(name, MAT_DIR,
                                  unreal.MaterialInstanceConstant, factory)
    if not mi:
        say("could not create instance %s" % name)
        return None
    mi.set_editor_property("parent", master)
    for param, tex in textures.items():
        try:
            MEL.set_material_instance_texture_parameter_value(mi, param, tex)
        except Exception as exc:
            say("instance %s param %s failed: %r" % (name, param, exc))
    if tint:
        MEL.set_material_instance_vector_parameter_value(
            mi, "BaseColorTint", unreal.LinearColor(tint[0], tint[1], tint[2], 1.0))
    MEL.set_material_instance_scalar_parameter_value(mi, "UVTiling", float(tiling))
    MEL.set_material_instance_scalar_parameter_value(mi, "EmissiveStrength", float(emissive))
    EAL.save_asset(path, only_if_is_dirty=False)
    say("instance ready: %s" % path)
    return mi


# Named instances consumed by ue5_art_pass.py. The key is the art-pass material
# name; the value is (source family, tint, UV tiling, emissive strength).
ART_PASS_INSTANCES = {
    "Stone": ("limestone", (1.00, 1.00, 1.00), 8.0, 0.0),
    "StoneDark": ("slate", (0.90, 0.95, 1.05), 6.0, 0.0),
    "StoneLight": ("limestone", (1.22, 1.18, 1.08), 8.0, 0.0),
    "StoneCold": ("slate", (0.82, 0.92, 1.15), 6.0, 0.0),
    "StoneWarm": ("limestone", (1.18, 0.98, 0.78), 8.0, 0.0),
    "Wood": ("walnut", (1.00, 1.00, 1.00), 4.0, 0.0),
    "Metal": ("blackened_iron", (1.00, 1.00, 1.00), 6.0, 0.0),
    "Gold": ("gold_trim", (1.00, 1.00, 1.00), 8.0, 0.0),
    "ClothRed": ("crimson_velvet", (1.00, 1.00, 1.00), 6.0, 0.0),
    "ClothBlue": ("crimson_velvet", (0.42, 0.55, 1.35), 6.0, 0.0),
    "Carpet": ("carpet", (1.00, 1.00, 1.00), 1.0, 0.0),
    "Foliage": ("moss", (1.00, 1.00, 1.00), 8.0, 0.0),
    "Water": ("water", (1.00, 1.00, 1.00), 4.0, 0.0),
    "Ice": ("ice", (1.00, 1.00, 1.00), 6.0, 0.0),
    "Lava": ("lava", (1.00, 1.00, 1.00), 6.0, 3.0),
    "Bone": ("limestone", (1.35, 1.30, 1.15), 4.0, 0.0),
}


def main():
    fams = families()
    say("families=%r" % fams)
    master = build_master()
    if not master:
        raise RuntimeError("master material creation failed")

    family_textures = {}
    for family in fams:
        dest = "%s/%s" % (TEX_ROOT, family)
        EAL.make_directory(dest)
        textures = {}
        mapping = {
            "A": ("BaseColorTex", True, unreal.TextureCompressionSettings.TC_DEFAULT),
            "N": ("NormalTex", False, unreal.TextureCompressionSettings.TC_NORMALMAP),
            "ORM": ("ORMTex", False, unreal.TextureCompressionSettings.TC_MASKS),
            "E": ("EmissiveTex", True, unreal.TextureCompressionSettings.TC_DEFAULT),
        }
        for suffix, (param, srgb, comp) in mapping.items():
            png = os.path.join(SOURCE, family, "T_%s_%s.png" % (family, suffix))
            if not os.path.exists(png):
                continue
            tex = import_texture(png, dest, "T_%s_%s" % (family, suffix), srgb, comp)
            if tex:
                textures[param] = tex
        family_textures[family] = textures
        build_instance(master, family, textures)

    # Named instances used by the art pass and by later material passes.
    for name, (family, tint, tiling, emissive) in ART_PASS_INSTANCES.items():
        textures = family_textures.get(family)
        if not textures:
            say("skip %s: missing family %s" % (name, family))
            continue
        build_instance(master, family, textures, name="MI_%s" % name, tint=tint,
                       tiling=tiling, emissive=emissive)

    say("import complete")


main()
