"""QA verification for generated content. Run as a PythonScript commandlet."""

import unreal

LOG = "[NA-QA] "
ERRORS = []


def log(msg):
    unreal.log(LOG + str(msg))


def err(msg):
    ERRORS.append(str(msg))
    unreal.log_error(LOG + str(msg))


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


def brief(value):
    if value is None:
        return "None"
    try:
        text = value.get_name()
        if text:
            return text
    except Exception:
        pass
    return str(value)[:120]


def check_asset(path):
    if not unreal.EditorAssetLibrary.does_asset_exist(path):
        err("missing asset " + path)
        return None
    return unreal.EditorAssetLibrary.load_asset(path)


TABLES = {
    "DT_WeaponDataTable": 19,
    "DT_MaterialDataTable": 40,
    "DT_WeaponRecipeTable": 19,
    "DT_WeaponRecipeTable_Complete": 19,
    "DT_WeaponMaterialRequirements": 19,
    "DT_InnocentDevilDataTable": 7,
    "DT_EnemyDataTable": 23,
    "DT_EnemyEncounterTable": 32,
    "DT_ItemDropTable": 50,
    "DT_InnocentDevilEvolutionTable": 14,
    "DT_ChapterProgressionTable": 10,
}

log("=== DATA TABLES ===")
for name, expected in TABLES.items():
    table = check_asset("/Game/DataTables/" + name)
    if not table:
        continue
    rows = table.get_row_names()
    if len(rows) != expected:
        err("%s has %d rows, expected %d" % (name, len(rows), expected))
    sample = rows[0] if rows else "<none>"
    log("%s: %d rows (expected %d), first=%s" % (name, len(rows), expected, sample))

    # Read a few columns to prove values (not just row names) survived.
    def column(column_name):
        try:
            values = unreal.DataTableFunctionLibrary.get_data_table_column_as_string(table, column_name)
            return values
        except Exception as exc:
            return ["<error: %r>" % exc]

    checks = {
        "DT_WeaponDataTable": ["BaseDamage", "DamageType", "ComboAnimCount"],
        "DT_MaterialDataTable": ["MaterialColor", "bIsRare"],
        "DT_WeaponRecipeTable": ["RequiredMaterials"],
        "DT_WeaponMaterialRequirements": ["Material1", "Material1Count"],
        "DT_InnocentDevilDataTable": ["EvolutionCrystalColor", "DevilType"],
        "DT_EnemyEncounterTable": ["Count", "IsBoss"],
        "DT_ChapterProgressionTable": ["SaveRoomCount", "GreenDoorRoomCount", "InnocentDevilAcquired"],
    }.get(name, [])
    for check in checks:
        values = column(check)
        log("  %s[0..2] = %s" % (check, values[:3]))

log("=== BLUEPRINTS ===")
BPS = {
    "BP_HectorCharacter": "/Game/Blueprints/Characters",
    "BP_EnemyBase": "/Game/Blueprints/Characters",
    "BP_BossBase": "/Game/Blueprints/Characters",
    "BP_InnocentDevilActor": "/Game/Blueprints/Characters",
    "BP_Room": "/Game/Blueprints/World",
    "BP_SaveRoom": "/Game/Blueprints/World",
    "BP_CandleBreakable": "/Game/Blueprints/World",
    "BP_ItemDrop": "/Game/Blueprints/World",
    "BP_MapChecker": "/Game/Blueprints/System",
    "BP_NobleArchimedesHUD": "/Game/Blueprints/UI",
    "BP_NobleHUDWidget": "/Game/Blueprints/UI",
    "BP_NobleArchimedesGameModeBase": "/Game/Blueprints/Core",
    "BP_NobleArchimedesPlayerController": "/Game/Blueprints/Core",
    "BP_NobleArchimedesGameInstance": "/Game/Blueprints/Core",
    "BP_Skeleton": "/Game/Blueprints/Characters",
    "BP_Zombie": "/Game/Blueprints/Characters",
    "BP_Ghoul": "/Game/Blueprints/Characters",
    "BP_SentinelKnight": "/Game/Blueprints/Characters",
}
BP_CLASSES = {}
for name, folder in BPS.items():
    bp = check_asset("%s/%s" % (folder, name))
    if not bp:
        continue
    try:
        cls = bp.generated_class()
    except Exception as exc:
        err("%s generated_class failed: %r" % (name, exc))
        continue
    if not cls:
        err("%s has no generated class" % name)
        continue
    BP_CLASSES[name] = cls
    log("%s -> %s" % (name, cls.get_name()))

log("=== CHARACTER DEFAULTS ===")
hector = BP_CLASSES.get("BP_HectorCharacter")
hector_cdo = None
if hector:
    cdo = unreal.get_default_object(hector)
    hector_cdo = cdo
    for prop in ("DefaultMappingContext", "MoveAction", "LookAction", "JumpAction",
                 "LightAttackAction", "HeavyAttackAction", "GuardAction", "DodgeAction",
                 "InteractAction", "SummonDevilAction", "CameraModeAction", "MapAction", "PauseAction",
                 "UseItemAction", "ForgeAction", "QuickSaveAction", "QuickLoadAction"):
        value = get_prop(cdo, prop)
        if not value:
            err("BP_HectorCharacter.%s is not set" % prop)
        else:
            log("  %s = %s" % (prop, brief(value)))
    mesh = get_prop(cdo, "Mesh")
    if mesh:
        log("  Mesh skeletal asset = %s" % brief(get_prop(mesh, "SkeletalMeshAsset")))

    combat = get_prop(cdo, "CombatComponent")
    if not combat:
        err("BP_HectorCharacter.CombatComponent is missing")
    else:
        weapon_table = get_prop(combat, "WeaponDataTableAsset")
        if not weapon_table:
            err("CombatComponent.WeaponDataTableAsset is not set")
        else:
            log("  WeaponDataTableAsset = %s" % brief(weapon_table))
        log("  DefaultWeaponName = %s" % get_prop(combat, "DefaultWeaponName"))

    devil_component = get_prop(cdo, "InnocentDevilComponent")
    if not devil_component:
        err("BP_HectorCharacter.InnocentDevilComponent is missing")
    else:
        devil_class = get_prop(devil_component, "DevilActorClass")
        if not devil_class:
            err("InnocentDevilComponent.DevilActorClass is not set")
        else:
            log("  DevilActorClass = %s" % brief(devil_class))

log("=== ENEMY ARCHETYPES ===")
EXPECTED_ENEMIES = {
    "BP_Skeleton": ("Skeleton", 50.0, 10.0, True),
    "BP_Zombie": ("Zombie", 80.0, 15.0, False),
    "BP_Ghoul": ("Ghoul", 60.0, 12.0, True),
    "BP_SentinelKnight": ("Castle Elite", 140.0, 35.0, True),
    "BP_BossBase": ("Final Boss", 500.0, 60.0, False),
}
for bp_name, (enemy_name, max_health, damage, can_steal) in EXPECTED_ENEMIES.items():
    cls = BP_CLASSES.get(bp_name)
    if not cls:
        continue
    cdo = unreal.get_default_object(cls)
    actual_name = str(get_prop(cdo, "EnemyName"))
    actual_health = get_prop(cdo, "MaxHealth")
    actual_damage = get_prop(cdo, "Damage")
    actual_steal = get_prop(cdo, "CanBeStolen")
    log("  %s: name=%s hp=%s damage=%s steal=%s" % (
        bp_name, actual_name, actual_health, actual_damage, actual_steal))
    if actual_name != enemy_name:
        err("%s EnemyName is %s, expected %s" % (bp_name, actual_name, enemy_name))
    if abs(float(actual_health) - max_health) > 0.01:
        err("%s MaxHealth is %s, expected %s" % (bp_name, actual_health, max_health))
    if abs(float(actual_damage) - damage) > 0.01:
        err("%s Damage is %s, expected %s" % (bp_name, actual_damage, damage))
    if bool(actual_steal) != can_steal:
        err("%s CanBeStolen is %s, expected %s" % (bp_name, actual_steal, can_steal))
    if not get_prop(cdo, "ItemDropClass"):
        err("%s ItemDropClass is not set" % bp_name)

for bp_name in ("BP_InnocentDevilActor", "BP_ItemDrop"):
    cls = BP_CLASSES.get(bp_name)
    if not cls:
        continue
    cdo = unreal.get_default_object(cls)
    mesh = get_prop(cdo, "Mesh") if bp_name == "BP_InnocentDevilActor" else get_prop(cdo, "ItemMesh")
    if not mesh:
        err("%s mesh component is missing" % bp_name)
        continue
    asset = get_prop(mesh, "SkeletalMeshAsset") if bp_name == "BP_InnocentDevilActor" else get_prop(mesh, "StaticMesh")
    if not asset:
        err("%s has no visible placeholder mesh" % bp_name)
    else:
        log("  %s mesh = %s" % (bp_name, brief(asset)))

candle_cls = BP_CLASSES.get("BP_CandleBreakable")
if candle_cls:
    candle_cdo = unreal.get_default_object(candle_cls)
    if not get_prop(candle_cdo, "ItemDropClass"):
        err("BP_CandleBreakable.ItemDropClass is not set")
    drops = get_prop(candle_cdo, "PossibleDrops") or []
    if "Iron Shard" not in [str(d) for d in drops]:
        err("BP_CandleBreakable does not drop Iron Shard")
    else:
        log("  BP_CandleBreakable drops = %s" % ", ".join(str(d) for d in drops))

log("=== GAME MODE DEFAULTS ===")
gm = BP_CLASSES.get("BP_NobleArchimedesGameModeBase")
if gm:
    cdo = unreal.get_default_object(gm)
    for prop in ("DefaultPawnClass", "PlayerControllerClass", "HUDClass"):
        value = get_prop(cdo, prop)
        if not value:
            err("GameMode.%s is not set" % prop)
        else:
            log("  %s = %s" % (prop, brief(value)))

hud = BP_CLASSES.get("BP_NobleArchimedesHUD")
if hud:
    hud_cdo = unreal.get_default_object(hud)
    widget_cls = get_prop(hud_cdo, "HUDWidgetClass")
    if not widget_cls:
        err("HUD.HUDWidgetClass is not set")
    else:
        log("  HUDWidgetClass = %s" % brief(widget_cls))

log("=== INPUT ===")
imc = check_asset("/Game/Input/IMC_Default")
if imc:
    try:
        data = imc.get_editor_property("default_key_mappings")
        mappings = data.get_editor_property("mappings")
        log("IMC_Default mappings: %d" % len(mappings))
        for index, mapping in enumerate(mappings):
            action = get_prop(mapping, "Action")
            key = get_prop(mapping, "Key")
            modifiers = get_prop(mapping, "Modifiers")
            log("  [%d] action=%s key=%s modifiers=%d" % (
                index, brief(action), brief(key), len(modifiers) if modifiers else 0))
        if len(mappings) < 25:
            err("IMC_Default has fewer mappings than expected (%d)" % len(mappings))
    except Exception as exc:
        err("Could not read IMC mappings: %r" % exc)

for action in ("IA_Move", "IA_Look", "IA_Jump", "IA_LightAttack", "IA_HeavyAttack",
               "IA_Guard", "IA_Dodge", "IA_Interact", "IA_SummonDevil", "IA_CameraMode",
               "IA_Map", "IA_Pause"):
    check_asset("/Game/Input/Actions/" + action)

log("=== LEVEL ===")
MAP_PATH = "/Game/Maps/Chap_01_AbandonedCastle"
LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
loaded = False
try:
    loaded = LES.load_level(MAP_PATH)
except Exception as exc:
    log("load_level failed: %r" % exc)
if not loaded:
    try:
        loaded = unreal.EditorLoadingAndSavingUtils.load_map(MAP_PATH)
    except Exception as exc:
        log("load_map failed: %r" % exc)
log("map loaded: %s" % loaded)

EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = EAS.get_all_level_actors()
log("total actors: %d" % len(actors))
counts = {}
for actor in actors:
    name = actor.get_class().get_name()
    counts[name] = counts.get(name, 0) + 1
for name in sorted(counts):
    log("  %s: %d" % (name, counts[name]))

rooms = [a for a in actors if a.get_class().get_name().startswith("BP_Room_C")]
log("room instances: %d" % len(rooms))
for room in rooms:
    log("  room=%s locked=%s save=%s boss=%s enemies=%s" % (
        get_prop(room, "RoomName"),
        get_prop(room, "bIsLocked"),
        get_prop(room, "bIsSaveRoom"),
        get_prop(room, "bIsBossArena"),
        len(get_prop(room, "EnemyClassesToSpawn") or []),
    ))

starts = [a for a in actors if isinstance(a, unreal.PlayerStart)]
log("player starts: %d" % len(starts))
for start in starts:
    log("  start at %s" % start.get_actor_location())

log("=== RESULT ===")
log("errors=%d" % len(ERRORS))
for message in ERRORS:
    log("ERROR: " + message)
