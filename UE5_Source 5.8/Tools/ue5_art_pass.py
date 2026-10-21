"""Noble Archimedes presentation pass (UE 5.8).

This script is deliberately asset-independent: it uses engine primitive meshes
and authored materials to turn the grey blockouts into readable gothic spaces.
It does not import, extract, or reference any original game assets.

Run with:
    UnrealEditor-Cmd.exe <project>.uproject -run=PythonScript -script=<this file> -unattended -nosplash -nop4
"""

import math
import re

import unreal

LOG_PREFIX = "[NA-ART] "
ART_TAG = "NA_ArtPass"
MAT_DIR = "/Game/Art/Materials"
GEN_MAT_DIR = "/Game/Art/Materials/Generated"

ASSET_TOOLS = unreal.AssetToolsHelpers.get_asset_tools()
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

CHAPTER_MAPS = {
    1: "Chap_01_AbandonedCastle",
    2: "Chap_02_BaljhetMountains",
    3: "Chap_03_GaribaldiTemple",
    4: "Chap_04_MortviaAqueduct",
    5: "Chap_05_ForestOfJigramunt",
    6: "Chap_06_CordovaTown",
    7: "Chap_07_EneomaosMachineTower",
    8: "Chap_08_AiolonRuins",
    9: "Chap_09_InfiniteCorridor",
    10: "Chap_10_DraculasCastle",
}

# wall/floor/accent/window/cloth are material names; the flags change the props
# that are generated for a chapter.
CHAPTER_STYLES = {
    1: {"wall": "Stone", "floor": "StoneDark", "accent": "Gold", "window": "WindowBlue",
        "cloth": "ClothRed", "fog": (0.10, 0.13, 0.20), "light": (0.55, 0.65, 0.95)},
    2: {"wall": "StoneCold", "floor": "StoneDark", "accent": "Bone", "window": "WindowBlue",
        "cloth": "ClothBlue", "fog": (0.12, 0.16, 0.22), "light": (0.45, 0.62, 1.0)},
    3: {"wall": "StoneWarm", "floor": "StoneDark", "accent": "Gold", "window": "WindowGold",
        "cloth": "ClothRed", "fog": (0.18, 0.14, 0.10), "light": (1.0, 0.78, 0.45)},
    4: {"wall": "StoneCold", "floor": "StoneDark", "accent": "Metal", "window": "WindowBlue",
        "cloth": "ClothBlue", "fog": (0.08, 0.14, 0.18), "light": (0.35, 0.75, 0.95),
        "water": True},
    5: {"wall": "Wood", "floor": "Foliage", "accent": "Bone", "window": "WindowGold",
        "cloth": "Foliage", "fog": (0.08, 0.15, 0.10), "light": (0.45, 0.85, 0.50),
        "foliage": True},
    6: {"wall": "StoneWarm", "floor": "StoneDark", "accent": "Gold", "window": "WindowGold",
        "cloth": "ClothRed", "fog": (0.16, 0.13, 0.10), "light": (1.0, 0.70, 0.40)},
    7: {"wall": "Metal", "floor": "StoneCold", "accent": "Gold", "window": "WindowGold",
        "cloth": "ClothBlue", "fog": (0.13, 0.10, 0.07), "light": (0.85, 0.55, 0.30)},
    8: {"wall": "StoneCold", "floor": "StoneDark", "accent": "Bone", "window": "WindowBlue",
        "cloth": "ClothBlue", "fog": (0.11, 0.11, 0.17), "light": (0.70, 0.55, 0.95)},
    9: {"wall": "StoneCold", "floor": "StoneDark", "accent": "Gold", "window": "WindowBlue",
        "cloth": "ClothBlue", "fog": (0.10, 0.09, 0.17), "light": (0.65, 0.40, 1.0)},
    10: {"wall": "Stone", "floor": "StoneDark", "accent": "Gold", "window": "WindowRed",
         "cloth": "ClothRed", "fog": (0.16, 0.06, 0.07), "light": (1.0, 0.30, 0.30)},
}

MATERIAL_SPECS = {
    "Stone": ((0.075, 0.070, 0.065), 0.90, 0.00, None, False),
    "StoneDark": ((0.035, 0.033, 0.030), 0.95, 0.00, None, False),
    "StoneLight": ((0.15, 0.14, 0.12), 0.85, 0.00, None, False),
    "StoneCold": ((0.060, 0.070, 0.085), 0.88, 0.00, None, False),
    "StoneWarm": ((0.135, 0.100, 0.070), 0.90, 0.00, None, False),
    "Wood": ((0.095, 0.040, 0.018), 0.80, 0.00, None, False),
    "Metal": ((0.045, 0.050, 0.060), 0.32, 0.90, None, False),
    "Gold": ((0.42, 0.25, 0.045), 0.25, 0.95, None, False),
    "Bone": ((0.52, 0.48, 0.38), 0.72, 0.00, None, False),
    "ClothRed": ((0.22, 0.012, 0.018), 0.86, 0.00, None, False),
    "ClothBlue": ((0.014, 0.025, 0.095), 0.86, 0.00, None, False),
    "Carpet": ((0.12, 0.020, 0.025), 0.94, 0.00, None, False),
    "Wax": ((0.55, 0.45, 0.25), 0.60, 0.00, None, False),
    "Foliage": ((0.025, 0.105, 0.040), 0.92, 0.00, None, False),
    "Water": ((0.012, 0.075, 0.14), 0.12, 0.20, None, False),
    "Flesh": ((0.17, 0.095, 0.085), 0.72, 0.00, None, False),
    "Armor": ((0.180, 0.195, 0.240), 0.32, 0.90, None, False),
    "Barrier": ((0.0, 0.0, 0.0), 0.4, 0.0, (4.0, 0.10, 0.05), True),
    "Flame": ((0.0, 0.0, 0.0), 0.4, 0.0, (7.0, 2.2, 0.30), True),
    "Portal": ((0.0, 0.0, 0.0), 0.4, 0.0, (1.2, 0.20, 3.5), True),
    "WindowBlue": ((0.0, 0.0, 0.0), 0.3, 0.0, (0.35, 1.20, 2.8), True),
    "WindowRed": ((0.0, 0.0, 0.0), 0.3, 0.0, (2.8, 0.20, 0.30), True),
    "WindowGold": ((0.0, 0.0, 0.0), 0.3, 0.0, (2.6, 1.35, 0.30), True),
    "Moon": ((0.0, 0.0, 0.0), 0.3, 0.0, (0.35, 0.45, 0.95), True),
}

MATERIALS = {}


def log(message):
    unreal.log(LOG_PREFIX + str(message))


def warn(message):
    unreal.log_warning(LOG_PREFIX + str(message))


def error(message):
    unreal.log_error(LOG_PREFIX + str(message))


def _prop_candidates(name):
    yield name
    yield name[:1].lower() + name[1:]
    snake = re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
    yield snake


def set_prop(obj, name, value):
    for candidate in _prop_candidates(name):
        try:
            obj.set_editor_property(candidate, value)
            return True
        except Exception:
            continue
    return False


def get_prop(obj, name, default=None):
    for candidate in _prop_candidates(name):
        try:
            return obj.get_editor_property(candidate)
        except Exception:
            continue
    return default


def ensure_material(name):
    # Prefer a generated PBR material instance when the Phase 4.0 kit is present.
    generated_path = "%s/MI_%s" % (GEN_MAT_DIR, name)
    if unreal.EditorAssetLibrary.does_asset_exist(generated_path):
        generated = unreal.EditorAssetLibrary.load_asset(generated_path)
        if generated:
            return generated

    path = "%s/%s" % (MAT_DIR, name)
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        material = unreal.EditorAssetLibrary.load_asset(path)
        if material:
            return material

    base_color, roughness, metallic, emissive, unlit = MATERIAL_SPECS[name]
    unreal.EditorAssetLibrary.make_directory(MAT_DIR)
    material = ASSET_TOOLS.create_asset(name, MAT_DIR, unreal.Material,
                                        unreal.MaterialFactoryNew())
    if not material:
        error("Could not create material %s" % name)
        return None

    # Character meshes are skeletal; without this flag the engine silently swaps
    # in the default material at runtime and logs a missing-usage warning.
    try:
        material.set_editor_property("used_with_skeletal_mesh", True)
    except Exception as exc:
        warn("could not flag %s for skeletal meshes: %s" % (name, exc))

    base = unreal.MaterialEditingLibrary.create_material_expression(
        material, unreal.MaterialExpressionVectorParameter, -360, 0)
    base.set_editor_property("parameter_name", "BaseColor")
    base.set_editor_property("default_value", unreal.LinearColor(
        base_color[0], base_color[1], base_color[2], 1.0))
    unreal.MaterialEditingLibrary.connect_material_property(
        base, "", unreal.MaterialProperty.MP_BASE_COLOR)

    rough = unreal.MaterialEditingLibrary.create_material_expression(
        material, unreal.MaterialExpressionScalarParameter, -360, 160)
    rough.set_editor_property("parameter_name", "Roughness")
    rough.set_editor_property("default_value", roughness)
    unreal.MaterialEditingLibrary.connect_material_property(
        rough, "", unreal.MaterialProperty.MP_ROUGHNESS)

    metal = unreal.MaterialEditingLibrary.create_material_expression(
        material, unreal.MaterialExpressionScalarParameter, -360, 240)
    metal.set_editor_property("parameter_name", "Metallic")
    metal.set_editor_property("default_value", metallic)
    unreal.MaterialEditingLibrary.connect_material_property(
        metal, "", unreal.MaterialProperty.MP_METALLIC)

    if emissive:
        glow = unreal.MaterialEditingLibrary.create_material_expression(
            material, unreal.MaterialExpressionVectorParameter, -360, 320)
        glow.set_editor_property("parameter_name", "Emissive")
        glow.set_editor_property("default_value", unreal.LinearColor(
            emissive[0], emissive[1], emissive[2], 1.0))
        unreal.MaterialEditingLibrary.connect_material_property(
            glow, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)

    if unlit:
        try:
            material.set_editor_property("shading_model",
                                         unreal.MaterialShadingModel.MSM_UNLIT)
        except Exception:
            pass

    unreal.MaterialEditingLibrary.recompile_material(material)
    unreal.EditorAssetLibrary.save_asset(path, only_if_is_dirty=False)
    log("Created material %s" % path)
    return material


def retint_material(name):
    """Push MATERIAL_SPECS values into an existing material asset in place.

    Deleting and recreating was unreliable: does_asset_exist() consults the
    asset registry, which is not populated at commandlet start, so the delete
    silently never ran and stale colours survived. The materials expose named
    parameters, so overwrite those instead and recompile.
    """
    path = "%s/%s" % (MAT_DIR, name)
    if not unreal.EditorAssetLibrary.does_asset_exist(path):
        return False
    mat = unreal.EditorAssetLibrary.load_asset(path)
    if not mat:
        return False

    base_color, roughness, metallic, emissive, unlit = MATERIAL_SPECS[name]
    changed = False

    try:
        if not mat.get_editor_property("used_with_skeletal_mesh"):
            mat.set_editor_property("used_with_skeletal_mesh", True)
            changed = True
    except Exception:
        pass

    for expr in unreal.MaterialEditingLibrary.get_material_expressions(mat):
        try:
            pname = str(expr.get_editor_property("parameter_name"))
        except Exception:
            continue
        if pname == "BaseColor":
            expr.set_editor_property("default_value", unreal.LinearColor(
                base_color[0], base_color[1], base_color[2], 1.0))
            changed = True
        elif pname == "Roughness":
            expr.set_editor_property("default_value", roughness)
            changed = True
        elif pname == "Metallic":
            expr.set_editor_property("default_value", metallic)
            changed = True
        elif pname == "Emissive" and emissive:
            expr.set_editor_property("default_value", unreal.LinearColor(
                emissive[0], emissive[1], emissive[2], 1.0))
            changed = True

    if changed:
        unreal.MaterialEditingLibrary.recompile_material(mat)
        unreal.EditorAssetLibrary.save_asset(path, only_if_is_dirty=False)
        log("  retinted %s" % path)
    return changed


def load_materials():
    for name in MATERIAL_SPECS:
        MATERIALS[name] = ensure_material(name)
        retint_material(name)


def clear_art_pass():
    for actor in EAS.get_all_level_actors():
        if actor.actor_has_tag(ART_TAG):
            EAS.destroy_actor(actor)


def load_map(map_name):
    path = "/Game/Maps/%s" % map_name
    if not unreal.EditorAssetLibrary.does_asset_exist(path):
        error("Missing map %s" % path)
        return False
    try:
        if LES.load_level(path):
            return True
    except Exception as exc:
        warn("load_level(%s) failed: %r" % (path, exc))
    try:
        return bool(unreal.EditorLoadingAndSavingUtils.load_map(path))
    except Exception as exc:
        error("load_map(%s) failed: %r" % (path, exc))
        return False


def save_map():
    try:
        if not LES.save_current_level():
            warn("save_current_level returned false")
    except Exception as exc:
        warn("save_current_level failed: %r" % exc)
        try:
            unreal.EditorLoadingAndSavingUtils.save_current_map()
        except Exception as exc2:
            error("save_current_map failed: %r" % exc2)


def spawn_actor(actor_class, label, location, rotation=(0.0, 0.0, 0.0)):
    actor = EAS.spawn_actor_from_class(
        actor_class, unreal.Vector(*location), unreal.Rotator(*rotation))
    if not actor:
        return None
    actor.set_actor_label(label)
    actor.set_editor_property("tags", [ART_TAG])
    return actor


def mesh_component(actor):
    if not actor:
        return None
    return get_prop(actor, "StaticMeshComponent")


def apply_material(actor, material):
    if not actor or not material:
        return
    comp = mesh_component(actor)
    if comp:
        comp.set_material(0, material)
        return
    for component in actor.get_components_by_class(unreal.StaticMeshComponent):
        component.set_material(0, material)


def spawn_mesh(label, mesh_path, location, scale, material, rotation=(0.0, 0.0, 0.0)):
    mesh = unreal.load_asset(mesh_path)
    if not mesh:
        warn("Missing engine mesh %s" % mesh_path)
        return None
    actor = spawn_actor(unreal.StaticMeshActor, label, location, rotation)
    if not actor:
        return None
    comp = mesh_component(actor)
    if not comp:
        return actor
    comp.set_static_mesh(mesh)
    comp.set_relative_scale3d(unreal.Vector(*scale))
    comp.set_mobility(unreal.ComponentMobility.STATIC)
    comp.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    if material:
        comp.set_material(0, material)
    return actor


def spawn_box(label, location, size, material, rotation=(0.0, 0.0, 0.0)):
    return spawn_mesh(label, "/Engine/BasicShapes/Cube.Cube", location,
                      (size[0] / 100.0, size[1] / 100.0, size[2] / 100.0),
                      material, rotation)


def spawn_cylinder(label, location, radius, height, material):
    return spawn_mesh(label, "/Engine/BasicShapes/Cylinder.Cylinder", location,
                      (radius / 50.0, radius / 50.0, height / 100.0), material)


def spawn_cone(label, location, radius, height, material):
    return spawn_mesh(label, "/Engine/BasicShapes/Cone.Cone", location,
                      (radius / 50.0, radius / 50.0, height / 100.0), material)


def spawn_sphere(label, location, radius, material):
    return spawn_mesh(label, "/Engine/BasicShapes/Sphere.Sphere", location,
                      (radius / 50.0, radius / 50.0, radius / 50.0), material)


def rgb_color(r, g, b, a=255):
    # Unreal Python's Color constructor is (B, G, R, A), unlike the C++ FColor
    # signature. Keep authored colors in RGB order and convert here.
    return unreal.Color(
        max(0, min(255, int(b))),
        max(0, min(255, int(g))),
        max(0, min(255, int(r))),
        max(0, min(255, int(a))))


def spawn_point_light(label, location, color, intensity, radius):
    actor = spawn_actor(unreal.PointLight, label, location)
    if not actor:
        return None
    comp = actor.get_component_by_class(unreal.PointLightComponent)
    if comp:
        set_prop(comp, "Intensity", intensity)
        set_prop(comp, "AttenuationRadius", radius)
        set_prop(comp, "LightColor", rgb_color(
            color[0] * 255,
            color[1] * 255,
            color[2] * 255))
        set_prop(comp, "CastShadows", True)
    return actor


def find_actors(prefix):
    result = []
    for actor in EAS.get_all_level_actors():
        label = actor.get_actor_label()
        if label and label.startswith(prefix):
            result.append(actor)
    return result


def make_scene_playable():
    """Finish the map so it renders and paths without an editor build step.

    Levels are authored from a commandlet, so Build Lighting and Build Paths
    never run: Chapter 1 shipped with 713 unbuilt light interactions (black,
    unlit geometry) and an unbuilt navmesh, which stops enemies from chasing.
    Making every light movable removes the dependency on a lighting build, and
    switching the navmesh to runtime generation removes the dependency on a
    paths build.
    """
    lights = 0
    navmeshes = 0
    for actor in EAS.get_all_level_actors():
        try:
            if isinstance(actor, unreal.WorldSettings):
                actor.set_editor_property("bForceNoPrecomputedLighting", True)
            elif isinstance(actor, unreal.RecastNavMesh):
                actor.set_editor_property(
                    "runtime_generation", unreal.RuntimeGenerationType.DYNAMIC)
                navmeshes += 1
            elif isinstance(actor, unreal.Light):
                if actor.root_component:
                    actor.root_component.set_mobility(
                        unreal.ComponentMobility.MOVABLE)
                    lights += 1
        except Exception as exc:
            warn("scene prep skipped %s: %s" % (actor.get_class().get_name(), exc))
    log("  scene prep: %d lights movable, %d navmesh runtime-dynamic" % (lights, navmeshes))


def dress_lock_barriers():
    """Give ARoom's lock barriers the glowing red material.

    Room.cpp creates four barrier components per room, hidden until the room
    locks. They had no material, so the "red bars" the design calls for rendered
    as default grey cubes. Barriers are components rather than actors, so they
    are found by component name.
    """
    barrier_material = MATERIALS.get("Barrier")
    if not barrier_material:
        warn("Barrier material unavailable; lock barriers stay untextured")
        return 0

    dressed = 0
    for actor in EAS.get_all_level_actors():
        try:
            components = actor.get_components_by_class(unreal.StaticMeshComponent)
        except Exception:
            continue
        for component in components:
            if str(component.get_name()).startswith("LockBarrier"):
                component.set_material(0, barrier_material)
                dressed += 1
    return dressed


def style_shell(style):
    wall = MATERIALS.get(style["wall"])
    floor = MATERIALS.get(style["floor"])
    for actor in find_actors("Floor_"):
        apply_material(actor, floor)
    for actor in find_actors("Corridor_"):
        apply_material(actor, floor)
    for actor in find_actors("WallNS_"):
        apply_material(actor, wall)
    for actor in find_actors("WallEW_"):
        apply_material(actor, wall)

    # Interior dressing built by the content pipeline (ceilings, columns and the
    # chapel altar) shares the chapter's palette instead of staying grey.
    for actor in find_actors("Ceiling_"):
        apply_material(actor, wall)
    for actor in find_actors("Column_"):
        apply_material(actor, wall)
    for actor in find_actors("AltarStep_"):
        apply_material(actor, floor)
    for actor in find_actors("Altar_"):
        apply_material(actor, MATERIALS.get(style["accent"]))

    # The generated point lights are intentionally dim fill lights; the art
    # pass adds warmer, localized braziers and window light.
    for actor in find_actors("Light_"):
        comp = actor.get_component_by_class(unreal.PointLightComponent)
        if comp:
            loc = actor.get_actor_location()
            actor.set_actor_location(unreal.Vector(loc.x, loc.y, 220.0), False, False)
            set_prop(comp, "Intensity", 160.0)
            set_prop(comp, "AttenuationRadius", 1600.0)
            set_prop(comp, "SourceRadius", 80.0)
            set_prop(comp, "CastShadows", False)
            # Keep a little colour identity but avoid an overpowering gel wash.
            set_prop(comp, "LightColor", rgb_color(
                (0.5 + style["light"][0] * 0.5) * 255,
                (0.5 + style["light"][1] * 0.5) * 255,
                (0.5 + style["light"][2] * 0.5) * 255))

    for actor in find_actors("Sun_"):
        comp = actor.get_component_by_class(unreal.DirectionalLightComponent)
        if comp:
            set_prop(comp, "Intensity", 0.35)
            set_prop(comp, "LightColor", rgb_color(
                style["light"][0] * 255,
                style["light"][1] * 255,
                style["light"][2] * 255))


def add_atmosphere(style, chapter):
    fog_actor = spawn_actor(unreal.ExponentialHeightFog, "Art_Fog_%02d" % chapter,
                            (0.0, 0.0, 200.0))
    if fog_actor:
        comp = fog_actor.get_component_by_class(unreal.ExponentialHeightFogComponent)
        if comp:
            set_prop(comp, "FogDensity", 0.008)
            set_prop(comp, "FogHeightFalloff", 0.16)
            set_prop(comp, "EnableVolumetricFog", True)
            set_prop(comp, "VolumetricFogExtinctionScale", 0.8)
            fog_color = unreal.LinearColor(style["fog"][0], style["fog"][1],
                                           style["fog"][2], 1.0)
            try:
                comp.set_fog_inscattering_color(fog_color)
            except Exception:
                set_prop(comp, "FogInscatteringLuminance", fog_color)

    sky = spawn_actor(unreal.SkyLight, "Art_SkyLight_%02d" % chapter, (0.0, 0.0, 2500.0))
    if sky:
        comp = sky.get_component_by_class(unreal.SkyLightComponent)
        if comp:
            set_prop(comp, "Intensity", 0.10)
            set_prop(comp, "LightColor", rgb_color(120, 150, 220))
            set_prop(comp, "RealTimeCapture", True)
            set_prop(comp, "VolumetricScatteringIntensity", 0.5)

    pp = spawn_actor(unreal.PostProcessVolume, "Art_PostProcess_%02d" % chapter,
                     (0.0, 0.0, 300.0))
    if pp:
        set_prop(pp, "Unbound", True)
        try:
            settings = pp.get_editor_property("settings")
            for prop, value in (
                ("bloom_intensity", 0.35),
                ("bloom_threshold", 1.2),
                ("vignette_intensity", 0.5),
                ("film_grain_intensity", 0.04),
                ("color_grading_intensity", 0.5),
                ("auto_exposure_bias", -0.25),
                ("auto_exposure_min_brightness", 0.08),
                ("auto_exposure_max_brightness", 2.0),
            ):
                try:
                    settings.set_editor_property("override_" + prop, True)
                except Exception:
                    pass
                try:
                    settings.set_editor_property(prop, value)
                except Exception:
                    pass
            pp.set_editor_property("settings", settings)
        except Exception as exc:
            warn("Post process setup failed: %r" % exc)


def add_room_architecture(cx, cy, sx, sy, height, style, chapter, room_index):
    wall = MATERIALS.get(style["wall"])
    accent = MATERIALS.get(style["accent"])
    cloth = MATERIALS.get(style["cloth"])
    window = MATERIALS.get(style["window"])

    inset = 170.0
    pillar_height = max(240.0, height - 30.0)
    for sign_x in (-1.0, 1.0):
        for sign_y in (-1.0, 1.0):
            px = cx + sign_x * (sx * 0.5 - inset)
            py = cy + sign_y * (sy * 0.5 - inset)
            spawn_cylinder("Art_Pillar_%02d_%d_%d_%d" % (chapter, room_index, sign_x > 0, sign_y > 0),
                           (px, py, pillar_height * 0.5), 34.0, pillar_height, wall)
            spawn_box("Art_Capital_%02d_%d_%d_%d" % (chapter, room_index, sign_x > 0, sign_y > 0),
                      (px, py, pillar_height - 12.0), (100.0, 100.0, 26.0), accent)

    # Ceiling slab keeps the camera from seeing an open void above the walls.
    spawn_box("Art_Ceiling_%02d_%d" % (chapter, room_index),
              (cx, cy, height - 8.0), (sx, sy, 18.0), MATERIALS.get("StoneDark"))

    # Wall banners and stained-glass panels.
    banner_y = cy + sy * 0.5 - 18.0
    for offset in (-0.28, 0.28):
        spawn_box("Art_Banner_%02d_%d_%+.2f" % (chapter, room_index, offset),
                  (cx + sx * offset, banner_y, 170.0), (120.0, 8.0, 260.0), cloth)
        spawn_box("Art_BannerTrim_%02d_%d_%+.2f" % (chapter, room_index, offset),
                  (cx + sx * offset, banner_y - 5.0, 305.0), (140.0, 8.0, 14.0), accent)

    spawn_box("Art_Window_%02d_%d_A" % (chapter, room_index),
              (cx - sx * 0.34, banner_y - 5.0, height * 0.58), (170.0, 6.0, 220.0), window)
    spawn_box("Art_Window_%02d_%d_B" % (chapter, room_index),
              (cx + sx * 0.34, banner_y - 5.0, height * 0.58), (170.0, 6.0, 220.0), window)

    # Framed doorway at the north wall.
    door_z = max(150.0, height * 0.42)
    for sign_x in (-1.0, 1.0):
        spawn_box("Art_DoorFrame_%02d_%d_%d" % (chapter, room_index, sign_x > 0),
                  (cx + sign_x * 205.0, banner_y - 12.0, door_z),
                  (45.0, 80.0, door_z * 2.0), accent)
    spawn_box("Art_DoorLintel_%02d_%d" % (chapter, room_index),
              (cx, banner_y - 12.0, door_z * 2.0 + 22.0), (455.0, 80.0, 45.0), accent)

    # Corner braziers.
    for sign_x, sign_y in ((-1.0, -1.0), (-1.0, 1.0), (1.0, -1.0), (1.0, 1.0)):
        bx = cx + sign_x * (sx * 0.5 - 240.0)
        by = cy + sign_y * (sy * 0.5 - 240.0)
        spawn_cylinder("Art_BrazierBowl_%02d_%d_%d_%d" % (chapter, room_index, sign_x > 0, sign_y > 0),
                       (bx, by, 60.0), 55.0, 55.0, MATERIALS.get("Metal"))
        spawn_cone("Art_BrazierFlame_%02d_%d_%d_%d" % (chapter, room_index, sign_x > 0, sign_y > 0),
                   (bx, by, 125.0), 35.0, 80.0, MATERIALS.get("Flame"))
        spawn_point_light("Art_BrazierLight_%02d_%d_%d_%d" % (chapter, room_index, sign_x > 0, sign_y > 0),
                          (bx, by, 180.0), (1.0, 0.55, 0.20), 650.0, 750.0)

    # A cloth runner is deferred until a dedicated carpet mesh/material is
    # authored. A scaled cube stretches the weave into a checker-like pattern
    # under the room fill lights, so the blockout keeps a clean stone floor.


def add_foliage(cx, cy, sx, sy, chapter, room_index):
    foliage = MATERIALS.get("Foliage")
    wood = MATERIALS.get("Wood")
    for index in range(6):
        angle = (2.0 * math.pi * index) / 6.0
        px = cx + math.cos(angle) * (sx * 0.30)
        py = cy + math.sin(angle) * (sy * 0.30)
        spawn_cylinder("Art_Tree_%02d_%d_%d" % (chapter, room_index, index),
                       (px, py, 120.0), 22.0, 240.0, wood)
        spawn_sphere("Art_Canopy_%02d_%d_%d" % (chapter, room_index, index),
                     (px, py, 300.0), 120.0, foliage)


def add_water(cx, cy, sx, sy, chapter, room_index):
    water = MATERIALS.get("Water")
    spawn_box("Art_Water_%02d_%d" % (chapter, room_index),
              (cx, cy, 8.0), (sx * 0.72, sy * 0.24, 8.0), water)


def add_save_shrine(cx, cy, chapter):
    spawn_box("Art_SaveAltar_%02d" % chapter, (cx, cy, 55.0),
              (240.0, 150.0, 110.0), MATERIALS.get("StoneLight"))
    spawn_box("Art_SaveAltarTop_%02d" % chapter, (cx, cy, 118.0),
              (280.0, 190.0, 18.0), MATERIALS.get("Gold"))
    spawn_cone("Art_SaveFlame_%02d" % chapter, (cx, cy, 190.0),
               35.0, 90.0, MATERIALS.get("Flame"))
    spawn_point_light("Art_SaveLight_%02d" % chapter, (cx, cy, 220.0),
                      (1.0, 0.72, 0.32), 700.0, 700.0)


def add_boss_dais(cx, cy, sy, chapter):
    spawn_box("Art_BossDais_%02d" % chapter, (cx, cy + sy * 0.28, 25.0),
              (520.0, 360.0, 50.0), MATERIALS.get("StoneLight"))
    spawn_box("Art_BossDaisTop_%02d" % chapter, (cx, cy + sy * 0.28, 55.0),
              (420.0, 280.0, 20.0), MATERIALS.get("Gold"))
    spawn_box("Art_BossThrone_%02d" % chapter, (cx, cy + sy * 0.40, 130.0),
              (190.0, 80.0, 240.0), MATERIALS.get("Stone"))
    spawn_box("Art_BossThroneBack_%02d" % chapter, (cx, cy + sy * 0.40 + 45.0, 250.0),
              (260.0, 30.0, 360.0), MATERIALS.get("ClothRed"))
    for sign in (-1.0, 1.0):
        spawn_cylinder("Art_BossPillar_%02d_%d" % (chapter, sign > 0),
                       (cx + sign * 470.0, cy + sy * 0.22, 230.0), 48.0, 460.0,
                       MATERIALS.get("Stone"))
        spawn_cone("Art_BossFlame_%02d_%d" % (chapter, sign > 0),
                   (cx + sign * 470.0, cy + sy * 0.22, 500.0), 45.0, 120.0,
                   MATERIALS.get("Flame"))
        spawn_point_light("Art_BossLight_%02d_%d" % (chapter, sign > 0),
                          (cx + sign * 470.0, cy + sy * 0.22, 540.0),
                          (1.0, 0.22, 0.15), 700.0, 900.0)


def dress_existing_actors(chapter, style):
    for actor in find_actors("Item_"):
        apply_material(actor, MATERIALS.get("Gold"))
    for actor in find_actors("Candle_"):
        apply_material(actor, MATERIALS.get("Wax"))
        location = actor.get_actor_location()
        spawn_cone("Art_CandleFlame_%02d_%s" % (chapter, actor.get_actor_label()),
                   (location.x, location.y, location.z + 72.0),
                   12.0, 38.0, MATERIALS.get("Flame"))
        spawn_point_light("Art_CandleLight_%02d_%s" % (chapter, actor.get_actor_label()),
                          (location.x, location.y, location.z + 90.0),
                          (1.0, 0.50, 0.16), 250.0, 350.0)
    for actor in find_actors("Portal_"):
        apply_material(actor, MATERIALS.get("Portal"))
        location = actor.get_actor_location()
        spawn_point_light("Art_PortalLight_%02d" % chapter,
                          (location.x, location.y, location.z + 120.0),
                          (0.45, 0.12, 1.0), 800.0, 900.0)


def tint_blueprint(folder, name, material, mesh_property="Mesh"):
    path = "%s/%s" % (folder, name)
    if not unreal.EditorAssetLibrary.does_asset_exist(path):
        return
    bp = unreal.EditorAssetLibrary.load_asset(path)
    if not bp:
        return
    try:
        cls = bp.generated_class()
    except Exception:
        cls = None
    if not cls:
        return
    cdo = unreal.get_default_object(cls)
    comp = get_prop(cdo, mesh_property)
    if not comp:
        return
    set_prop(comp, "OverrideMaterials", [material])
    unreal.EditorAssetLibrary.save_asset(path, only_if_is_dirty=False)


def tint_characters():
    tint_blueprint("/Game/Blueprints/Characters", "BP_HectorCharacter",
                   MATERIALS.get("Armor"))
    tint_blueprint("/Game/Blueprints/Characters", "BP_Skeleton", MATERIALS.get("Bone"))
    tint_blueprint("/Game/Blueprints/Characters", "BP_Zombie", MATERIALS.get("Flesh"))
    tint_blueprint("/Game/Blueprints/Characters", "BP_Ghoul", MATERIALS.get("Bone"))
    tint_blueprint("/Game/Blueprints/Characters", "BP_SentinelKnight", MATERIALS.get("Armor"))
    tint_blueprint("/Game/Blueprints/Characters", "BP_InnocentDevilActor",
                   MATERIALS.get("Portal"))
    tint_blueprint("/Game/Blueprints/World", "BP_ItemDrop",
                   MATERIALS.get("Gold"), "ItemMesh")
    tint_blueprint("/Game/Blueprints/World", "BP_CandleBreakable",
                   MATERIALS.get("Wax"), "CandleMesh")
    tint_blueprint("/Game/Blueprints/World", "BP_ChapterPortal",
                   MATERIALS.get("Portal"), "PortalMesh")


def build_chapter(chapter):
    map_name = CHAPTER_MAPS[chapter]
    style = CHAPTER_STYLES[chapter]
    if not load_map(map_name):
        return False

    clear_art_pass()
    style_shell(style)
    add_atmosphere(style, chapter)

    entry = (0.0, 0.0, 2200.0, 2200.0, 420.0)
    mid = (0.0, 2800.0, 1800.0, 1800.0, 520.0)
    save = (-2800.0, 0.0, 900.0, 900.0, 320.0)
    boss = (0.0, 5600.0, 2800.0, 2800.0, 620.0)

    for index, room in enumerate((entry, mid, save, boss)):
        cx, cy, sx, sy, height = room
        add_room_architecture(cx, cy, sx, sy, height, style, chapter, index)

    if style.get("foliage"):
        add_foliage(entry[0], entry[1], entry[2], entry[3], chapter, 0)
        add_foliage(mid[0], mid[1], mid[2], mid[3], chapter, 1)
    if style.get("water"):
        add_water(entry[0], entry[1], entry[2], entry[3], chapter, 0)

    add_save_shrine(save[0], save[1], chapter)
    add_boss_dais(boss[0], boss[1], boss[3], chapter)

    # Torches along the connecting corridors.
    for index, (x, y) in enumerate(((0.0, -1450.0), (0.0, 1450.0), (0.0, 3750.0),
                                     (-1550.0, 0.0), (1550.0, 0.0))):
        spawn_cone("Art_CorridorFlame_%02d_%d" % (chapter, index),
                   (x, y, 230.0), 20.0, 55.0, MATERIALS.get("Flame"))
        spawn_point_light("Art_CorridorLight_%02d_%d" % (chapter, index),
                          (x, y, 260.0), (1.0, 0.55, 0.20), 400.0, 550.0)

    dress_existing_actors(chapter, style)
    barriers = dress_lock_barriers()
    if barriers:
        log("  chapter %d: dressed %d lock barriers" % (chapter, barriers))
    make_scene_playable()
    save_map()
    log("Dressed chapter %d (%s)" % (chapter, map_name))
    return True


def main():
    load_materials()
    tint_characters()
    for chapter in sorted(CHAPTER_MAPS):
        build_chapter(chapter)
    log("Presentation pass complete")


main()
