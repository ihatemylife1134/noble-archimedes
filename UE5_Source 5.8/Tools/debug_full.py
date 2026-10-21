#!/usr/bin/env python3
"""Full gameplay debug audit.

Checks every link that has silently broken a playtest before: enemies without a
mesh, missing AnimClass, unassigned montages, unwired rooms, input actions with
no mappings, and materials not flagged for skeletal meshes.

Prints [NA-DEBUG] lines and a final RESULT so the quality gate can read it.
"""
import unreal

ISSUES = []
CHECKS = 0
CHAR_DIR = "/Game/Blueprints/Characters"


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


def check(ok, label, detail=""):
    global CHECKS
    CHECKS += 1
    status = "OK  " if ok else "FAIL"
    unreal.log("[NA-DEBUG] %s %s%s" % (status, label,
                                       (" -- " + detail) if detail and not ok else ""))
    if not ok:
        ISSUES.append("%s%s" % (label, (" (" + detail + ")") if detail else ""))
    return ok


def cdo_of(folder, name):
    path = "%s/%s" % (folder, name)
    if not unreal.EditorAssetLibrary.does_asset_exist(path):
        return None
    bp = unreal.EditorAssetLibrary.load_asset(path)
    try:
        return unreal.get_default_object(bp.generated_class())
    except Exception:
        return None


# --- enemies -------------------------------------------------------------
ENEMIES = ["BP_Skeleton", "BP_Zombie", "BP_Ghoul", "BP_SentinelKnight"]
for name in ENEMIES:
    cdo = cdo_of(CHAR_DIR, name)
    if not check(cdo is not None, "%s exists" % name):
        continue
    mesh = get_prop(cdo, "Mesh")
    check(mesh is not None, "%s has Mesh component" % name)
    skel = get_prop(mesh, "SkeletalMeshAsset") if mesh else None
    check(skel is not None, "%s has a skeletal mesh (was invisible)" % name,
          "assign one in the art pass")
    anim = get_prop(mesh, "AnimClass") if mesh else None
    check(anim is not None, "%s has AnimClass" % name, "enemies will T-pose")
    health = get_prop(cdo, "MaxHealth")
    check(health and health > 0, "%s MaxHealth set" % name, str(health))

# --- Hector --------------------------------------------------------------
hector = cdo_of(CHAR_DIR, "BP_HectorCharacter")
if check(hector is not None, "BP_HectorCharacter exists"):
    mesh = get_prop(hector, "Mesh")
    check(mesh is not None, "Hector Mesh component")
    check(get_prop(mesh, "SkeletalMeshAsset") is not None, "Hector skeletal mesh")
    check(get_prop(mesh, "AnimClass") is not None, "Hector AnimClass")
    for prop in ("DefaultMappingContext", "MoveAction", "LookAction", "JumpAction",
                 "LightAttackAction", "HeavyAttackAction", "DodgeAction"):
        check(get_prop(hector, prop) is not None, "Hector %s assigned" % prop)
    combat = get_prop(hector, "CombatComponent")
    if combat:
        hp = get_prop(combat, "MaxHealth")
        check(hp and hp >= 300, "Hector MaxHealth survivable", "got %s" % hp)

# --- input mappings ------------------------------------------------------
imc_path = "/Game/Input/IMC_Default"
if check(unreal.EditorAssetLibrary.does_asset_exist(imc_path), "IMC_Default exists"):
    imc = unreal.EditorAssetLibrary.load_asset(imc_path)
    # Mappings is protected on UInputMappingContext and the Python get_mappings()
    # call returns an empty array in this build, so the project exposes read
    # accessors for verification.
    try:
        count = unreal.NobleInputBuilder.get_mapping_count(imc)
        names = [str(n) for n in unreal.NobleInputBuilder.get_mapped_action_names(imc)]
    except Exception as exc:
        count, names = -1, []
        unreal.log_warning("[NA-DEBUG] input reader unavailable: %s" % exc)
    check(count >= 10, "IMC_Default has key mappings", "%d mappings" % count)
    for required in ("IA_Move", "IA_Look", "IA_LightAttack", "IA_HeavyAttack"):
        check(required in names, "%s mapped in IMC_Default" % required,
              "mapped: %s" % names)

# --- materials -----------------------------------------------------------
import os  # noqa: E402
for mat in ("Armor", "Bone", "Flesh"):
    path = "/Game/Art/Materials/%s" % mat
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        asset = unreal.EditorAssetLibrary.load_asset(path)
        check(bool(get_prop(asset, "used_with_skeletal_mesh")),
              "%s flagged for skeletal meshes" % mat,
              "character would fall back to default material")

# --- chapter 1 rooms -----------------------------------------------------
LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
if LES.load_level("/Game/Maps/Chap_01_AbandonedCastle"):
    total_enemies = 0
    rooms = 0
    for actor in EAS.get_all_level_actors():
        if not actor.get_class().get_name().startswith("BP_Room"):
            continue
        rooms += 1
        name = str(get_prop(actor, "RoomName"))
        classes = get_prop(actor, "EnemyClassesToSpawn") or []
        locs = get_prop(actor, "EnemySpawnLocations") or []
        total_enemies += len(classes)
        if len(classes):
            check(len(locs) == len(classes),
                  "%s spawn locations match classes" % name,
                  "%d classes vs %d locations" % (len(classes), len(locs)))
            for cls in classes:
                check(cls is not None, "%s enemy class resolved" % name)
        box = get_prop(actor, "RoomTriggerBox")
        if box:
            ext = box.get_editor_property("box_extent")
            check(ext.x > 100 and ext.y > 100, "%s trigger sized" % name)
    check(rooms == 4, "Chapter 1 has 4 rooms", "found %d" % rooms)
    check(total_enemies == 8, "Chapter 1 encounter total is 8",
          "found %d" % total_enemies)
else:
    check(False, "Chapter 1 map loads")

unreal.log("[NA-DEBUG] checks=%d issues=%d" % (CHECKS, len(ISSUES)))
for issue in ISSUES:
    unreal.log_warning("[NA-DEBUG] ISSUE: %s" % issue)
unreal.log("[NA-DEBUG] RESULT=%s" % ("PASS" if not ISSUES else "FAIL"))
