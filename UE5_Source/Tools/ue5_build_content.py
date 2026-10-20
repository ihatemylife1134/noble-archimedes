"""
Noble Archimedes content pipeline (UE 5.8).

Run with:
    UnrealEditor-Cmd.exe <project>.uproject -run=PythonScript -script=<this file> -unattended -nosplash

Creates/updates:
  /Game/DataTables/DT_*          - all 11 CSV data tables
  /Game/Blueprints/...           - core Blueprints from the C++ classes
  /Game/Input/Actions/IA_*       - Enhanced Input actions
  /Game/Input/IMC_Default        - default mapping context
  /Game/Maps/Chap_01_...         - Chapter 1 blockout

The script is idempotent for Blueprints and input assets. Data tables are
recreated so struct changes are picked up; nothing references them yet.
"""

import csv
import json
import os
import re
import traceback

import unreal

LOG_PREFIX = "[NA-CONTENT] "

CONTENT_DIR = unreal.SystemLibrary.get_project_content_directory()
DATA_TABLE_DIR = os.path.join(CONTENT_DIR, "DataTables")
MANIFEST_PATH = os.path.join(DATA_TABLE_DIR, "ImportManifest.json")

ASSET_TOOLS = unreal.AssetToolsHelpers.get_asset_tools()
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

STATS = {"created": 0, "updated": 0, "skipped": 0, "errors": 0}
ERRORS = []
BP_OBJECTS = {}


def log(message):
    unreal.log(LOG_PREFIX + str(message))


def warn(message):
    unreal.log_warning(LOG_PREFIX + str(message))


def error(message):
    STATS["errors"] += 1
    ERRORS.append(str(message))
    unreal.log_error(LOG_PREFIX + str(message))


def snake(name):
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def set_prop(obj, name, value, required=False):
    """Set an editor property, accepting PascalCase or snake_case names."""
    for candidate in (snake(name), name):
        try:
            obj.set_editor_property(candidate, value)
            return True
        except Exception:
            continue
    if required:
        error("Could not set property '%s' on %r" % (name, obj))
    return False


def get_prop(obj, name, default=None):
    for candidate in (snake(name), name):
        try:
            return obj.get_editor_property(candidate)
        except Exception:
            continue
    return default


def asset_path(folder, name):
    return "%s/%s" % (folder, name)


def load_asset(path):
    return unreal.EditorAssetLibrary.load_asset(path)


def save_asset(path):
    if not unreal.EditorAssetLibrary.save_asset(path, only_if_is_dirty=False):
        warn("Failed to save asset: %s" % path)


def compile_blueprint(bp):
    try:
        unreal.KismetEditorUtilities.compile_blueprint(bp)
        return True
    except Exception:
        try:
            unreal.BlueprintEditorLibrary.compile_blueprint(bp)
            return True
        except Exception as exc:
            warn("Could not compile %r: %r" % (bp, exc))
            return False


def ensure_blueprint(name, folder, parent_path):
    """Create a Blueprint if it does not exist. Returns the Blueprint asset."""
    path = asset_path(folder, name)
    if name in BP_OBJECTS:
        STATS["skipped"] += 1
        return BP_OBJECTS[name]

    existing = load_asset(path) if unreal.EditorAssetLibrary.does_asset_exist(path) else None
    if existing:
        BP_OBJECTS[name] = existing
        compile_blueprint(existing)
        STATS["skipped"] += 1
        return existing

    parent = unreal.load_class(None, parent_path)
    if not parent and not parent_path.endswith("_C"):
        parent = unreal.load_class(None, "%s.%s_C" % (parent_path, parent_path.rsplit("/", 1)[-1]))
    if not parent:
        error("Missing parent class for %s: %s" % (name, parent_path))
        return None

    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", parent)
    bp = ASSET_TOOLS.create_asset(name, folder, unreal.Blueprint, factory)
    if not bp:
        error("Failed to create Blueprint %s" % path)
        return None

    BP_OBJECTS[name] = bp
    compile_blueprint(bp)
    save_asset(path)
    STATS["created"] += 1
    log("Created Blueprint %s" % path)
    return bp


def bp_class(path, name):
    bp = BP_OBJECTS.get(name)
    if bp:
        try:
            cls = bp.generated_class()
            if cls:
                return cls
        except Exception:
            pass

    full = "%s.%s_C" % (path, name)
    cls = unreal.load_class(None, full)
    if not cls:
        cls = unreal.load_object(None, full)
    if not cls:
        try:
            cls = unreal.EditorAssetLibrary.load_blueprint_class(asset_path(path, name))
        except Exception:
            cls = None
    return cls


INPUT_CACHE = {}


def create_input_action(name, value_type):
    path = asset_path("/Game/Input/Actions", name)
    existing = INPUT_CACHE.get(name)
    if not existing and unreal.EditorAssetLibrary.does_asset_exist(path):
        existing = load_asset(path)
    if existing:
        ia = existing
        STATS["updated"] += 1
    else:
        factory = unreal.InputAction_Factory()
        ia = ASSET_TOOLS.create_asset(name, "/Game/Input/Actions", unreal.InputAction, factory)
        STATS["created"] += 1

    if not ia:
        error("Failed to create Input Action %s" % name)
        return None

    INPUT_CACHE[name] = ia
    ia.set_editor_property("value_type", value_type)
    save_asset(path)
    return ia


IMC_CACHE = {}


def create_mapping_context(name):
    path = asset_path("/Game/Input", name)
    existing = IMC_CACHE.get(name)
    if not existing and unreal.EditorAssetLibrary.does_asset_exist(path):
        existing = load_asset(path)
    if existing:
        imc = existing
        STATS["updated"] += 1
    else:
        factory = unreal.InputMappingContext_Factory()
        imc = ASSET_TOOLS.create_asset(name, "/Game/Input", unreal.InputMappingContext, factory)
        STATS["created"] += 1

    if not imc:
        error("Failed to create Input Mapping Context %s" % name)
    IMC_CACHE[name] = imc
    return imc


# ---------------------------------------------------------------------------
# Data tables
# ---------------------------------------------------------------------------

INT_FIELDS = {
    "Chapter", "Count", "Level", "Experience", "Health", "MaxHealth", "Attack",
    "ForgeLevel", "EvoCrystalCount", "Material1Count", "Material2Count",
    "Material3Count", "Material4Count", "ComboAnimCount", "FinalAttackAnimCount",
    "SaveRoomCount", "GreenDoorRoomCount",
}

FLOAT_FIELDS = {
    "AttackRange", "AttackSpeed", "BaseDamage", "Damage", "DetectionRange",
    "RespawnTime", "DropChance", "AttackPower",
}

BOOL_FIELDS = {
    "IsBoss", "Stealable", "CanBeStolen", "bIsUnlocked", "bIsEvolved",
    "IsStealOnly", "IsRare", "bIsRare",
}

ENUM_FIELDS = {
    "WeaponType", "DamageType", "EvoCrystalColor", "DevilType",
    "InnocentDevilAcquired", "EvolutionCrystalColor",
}

# csv column -> struct property when the names differ
RENAMES = {
    "SaveRooms": "SaveRoomCount",
    "GreenDoorRooms": "GreenDoorRoomCount",
}

TABLE_CONFIG = {
    "WeaponDataTable.csv": {"key": ["WeaponName"]},
    "MaterialDataTable.csv": {
        "key": ["MaterialName"],
        "color": {"MaterialColor": ["MaterialColorR", "MaterialColorG", "MaterialColorB", "MaterialColorA"]},
        "skip": ["MaterialColorR", "MaterialColorG", "MaterialColorB", "MaterialColorA"],
        "renames": {"IsRare": "bIsRare"},
    },
    "WeaponRecipeTable.csv": {"key": ["WeaponName"], "array": ["RequiredMaterials"]},
    "WeaponRecipeTable_Complete.csv": {
        "key": ["WeaponName"],
        "array": ["RequiredMaterials"],
        "skip": ["AttackPower", "AttackSpeed", "AttackRange", "EvoCrystalColor"],
    },
    "WeaponMaterialRequirements.csv": {"key": ["WeaponName"]},
    "InnocentDevilDataTable.csv": {"key": ["DevilName"]},
    "EnemyDataTable.csv": {"key": ["EnemyName"]},
    "EnemyEncounterTable.csv": {"key": ["Chapter", "EnemyName"]},
    "ItemDropTable.csv": {"key": ["EnemyName", "ItemName"]},
    "InnocentDevilEvolutionTable.csv": {"key": ["DevilName", "Level"]},
    "ChapterProgressionTable.csv": {"key": ["Chapter"]},
}


def parse_value(field, raw, cfg):
    value = (raw or "").strip()
    if value == "":
        return None

    if field in cfg.get("array", []):
        return [part.strip() for part in value.split(";") if part.strip()]

    if field in BOOL_FIELDS:
        return value.lower() in ("true", "1", "yes")
    if field in INT_FIELDS:
        try:
            return int(float(value))
        except ValueError:
            warn("Bad int '%s' for %s; keeping 0" % (value, field))
            return 0
    if field in FLOAT_FIELDS:
        try:
            return float(value)
        except ValueError:
            warn("Bad float '%s' for %s; keeping 0.0" % (value, field))
            return 0.0
    return value


def read_csv(path):
    with open(path, "r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def build_rows(csv_file, rows, cfg):
    key_columns = cfg["key"]
    result = {}
    used = {}

    for index, row in enumerate(rows):
        clean = {}
        for key, value in row.items():
            if key is None:
                continue
            if isinstance(value, list):
                value = value[0] if value else ""
            clean[key.strip()] = (value or "").strip()
        row = clean

        key_parts = [row.get(column, "") for column in key_columns]
        base_key = "_".join(part for part in key_parts if part) or "Row_%03d" % index
        used[base_key] = used.get(base_key, 0) + 1
        row_key = base_key if used[base_key] == 1 else "%s_%d" % (base_key, used[base_key])
        row_key = re.sub(r"[^A-Za-z0-9_\- ]", "_", row_key)

        payload = {}
        skip = set(cfg.get("skip", []))
        color_specs = cfg.get("color", {})
        renames = cfg.get("renames", {})

        for column, raw in row.items():
            if not column or column in skip:
                continue
            field = renames.get(column, RENAMES.get(column, column))
            value = parse_value(field, raw, cfg)
            if value is None:
                continue
            payload[field] = value

        for property_name, components in color_specs.items():
            values = []
            for component in components:
                raw = row.get(component, "").strip()
                try:
                    values.append(float(raw) if raw else 0.0)
                except ValueError:
                    values.append(0.0)
            if any(v != 0.0 for v in values):
                payload[property_name] = {
                    "R": values[0], "G": values[1], "B": values[2],
                    "A": values[3] if len(values) > 3 else 1.0,
                }

        result[row_key] = payload

    return result


def import_data_table(csv_file, struct_name, suggested_name):
    csv_path = os.path.join(DATA_TABLE_DIR, csv_file)
    if not os.path.exists(csv_path):
        error("Missing CSV: %s" % csv_path)
        return

    struct_path = "/Script/NobleArchimedes.%s" % (struct_name[1:] if struct_name.startswith("F") else struct_name)
    struct_obj = unreal.load_object(None, struct_path)
    if not struct_obj:
        error("Missing struct %s (%s)" % (struct_name, struct_path))
        return

    cfg = TABLE_CONFIG.get(csv_file, {"key": []})
    rows = read_csv(csv_path)
    payload_rows = build_rows(csv_file, rows, cfg)
    if not payload_rows:
        error("No rows parsed from %s" % csv_file)
        return

    folder = "/Game/DataTables"
    path = asset_path(folder, suggested_name)

    # Refill in place. The asset keeps a stable path so Blueprint references
    # survive re-imports. If a future C++ change alters a row struct's memory
    # layout (not just enum values), delete the asset once and rerun.
    table = None
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        table = load_asset(path)
        if table:
            # The JSON importer replaces matching row names, so stable CSVs
            # can be refilled in place without touching the asset identity.
            STATS["updated"] += 1

    if not table:
        factory = unreal.DataTableFactory()
        factory.set_editor_property("struct", struct_obj)
        table = ASSET_TOOLS.create_asset(suggested_name, folder, unreal.DataTable, factory)
        STATS["created"] += 1
    if not table:
        error("Failed to create DataTable %s" % path)
        return

    # UE's JSON DataTable importer expects a top-level array of row objects and
    # reads the row name from the "Name" field (ImportKeyField defaults to
    # "Name"). The key field is skipped when matching struct properties.
    json_rows = []
    for row_key, payload in payload_rows.items():
        entry = {"Name": row_key}
        entry.update(payload)
        json_rows.append(entry)

    json_text = json.dumps(json_rows, indent=2)
    ok = unreal.DataTableFunctionLibrary.fill_data_table_from_json_string(table, json_text)
    if not ok:
        error("JSON import failed for %s" % suggested_name)
        return

    table.modify()
    actual_rows = table.get_row_names()
    if len(actual_rows) != len(payload_rows):
        error("%s imported %d of %d rows" % (suggested_name, len(actual_rows), len(payload_rows)))
        return

    unreal.EditorAssetLibrary.save_loaded_asset(table, only_if_is_dirty=False)
    log("Imported %s: %d rows -> %s" % (csv_file, len(actual_rows), path))


def import_all_data_tables():
    if not os.path.exists(MANIFEST_PATH):
        error("Missing manifest: %s" % MANIFEST_PATH)
        return

    with open(MANIFEST_PATH, "r", encoding="utf-8") as handle:
        manifest = json.load(handle)

    for entry in manifest.get("tables", []):
        import_data_table(entry["csv_file"], entry["struct_name"], entry["suggested_name"])


# ---------------------------------------------------------------------------
# Blueprints
# ---------------------------------------------------------------------------

BLUEPRINTS = [
    ("BP_HectorCharacter", "/Game/Blueprints/Characters", "/Script/NobleArchimedes.HectorCharacter"),
    ("BP_EnemyBase", "/Game/Blueprints/Characters", "/Script/NobleArchimedes.EnemyBase"),
    ("BP_BossBase", "/Game/Blueprints/Characters", "/Script/NobleArchimedes.BossBase"),
    ("BP_InnocentDevilActor", "/Game/Blueprints/Characters", "/Script/NobleArchimedes.InnocentDevilActor"),
    ("BP_Room", "/Game/Blueprints/World", "/Script/NobleArchimedes.Room"),
    ("BP_SaveRoom", "/Game/Blueprints/World", "/Script/NobleArchimedes.SaveRoom"),
    ("BP_CandleBreakable", "/Game/Blueprints/World", "/Script/NobleArchimedes.CandleBreakable"),
    ("BP_ItemDrop", "/Game/Blueprints/World", "/Script/NobleArchimedes.ItemDrop"),
    ("BP_MapChecker", "/Game/Blueprints/System", "/Script/NobleArchimedes.MapChecker"),
    ("BP_NobleArchimedesHUD", "/Game/Blueprints/UI", "/Script/NobleArchimedes.NobleArchimedesHUD"),
    ("BP_NobleHUDWidget", "/Game/Blueprints/UI", "/Script/NobleArchimedes.NobleHUDWidget"),
    ("BP_NobleArchimedesGameModeBase", "/Game/Blueprints/Core", "/Script/NobleArchimedes.NobleArchimedesGameModeBase"),
    ("BP_NobleArchimedesPlayerController", "/Game/Blueprints/Core", "/Script/NobleArchimedes.NobleArchimedesPlayerController"),
    ("BP_NobleArchimedesGameInstance", "/Game/Blueprints/Core", "/Script/NobleArchimedes.NobleArchimedesGameInstance"),
]

# Chapter 1 enemy archetypes. The CSV row is the source of truth for stats;
# the Blueprint only supplies the class and the mesh.
ENEMY_ARCHETYPES = {
    "BP_Skeleton": ("BP_EnemyBase", "Skeleton"),
    "BP_Zombie": ("BP_EnemyBase", "Zombie"),
    "BP_Ghoul": ("BP_EnemyBase", "Ghoul"),
    "BP_SentinelKnight": ("BP_BossBase", "Castle Elite"),
}


def load_enemy_stats():
    path = os.path.join(DATA_TABLE_DIR, "EnemyDataTable.csv")
    if not os.path.exists(path):
        error("Missing enemy stats CSV: %s" % path)
        return {}
    return {row["EnemyName"]: row for row in read_csv(path)}


def apply_enemy_stats(cdo, row, drop_class, is_boss=False):
    if not row:
        return False

    set_prop(cdo, "EnemyName", row["EnemyName"])
    set_prop(cdo, "ChapterNumber", int(float(row.get("Chapter", 1))))
    health = float(row.get("Health", 50.0))
    set_prop(cdo, "Health", health)
    set_prop(cdo, "MaxHealth", health)
    set_prop(cdo, "Damage", float(row.get("Damage", 10.0)))
    set_prop(cdo, "AttackRange", float(row.get("AttackRange", 150.0)))
    set_prop(cdo, "DetectionRange", float(row.get("DetectionRange", 600.0)))
    set_prop(cdo, "Weaknesses", row.get("Weaknesses", ""))
    set_prop(cdo, "Tolerances", row.get("Tolerances", ""))
    set_prop(cdo, "ItemDrops", row.get("ItemDrops", ""))
    can_steal = str(row.get("CanBeStolen", "false")).lower() == "true"
    set_prop(cdo, "CanBeStolen", can_steal)
    set_prop(cdo, "bIsBoss", bool(is_boss))

    drops = [part.strip() for part in row.get("ItemDrops", "").split(";")
             if part.strip() and part.strip().lower() != "none"]
    if can_steal and drops:
        set_prop(cdo, "StealItem", drops[0])

    if drop_class:
        set_prop(cdo, "ItemDropClass", drop_class)
    return True


def create_all_blueprints():
    for name, folder, parent in BLUEPRINTS:
        ensure_blueprint(name, folder, parent)

    enemy_stats = load_enemy_stats()
    drop_class = bp_class("/Game/Blueprints/World", "BP_ItemDrop")

    # Base classes keep the drop class so every child can spawn loot.
    for base_name in ("BP_EnemyBase", "BP_BossBase"):
        base_cls = bp_class("/Game/Blueprints/Characters", base_name)
        if base_cls and drop_class:
            set_prop(unreal.get_default_object(base_cls), "ItemDropClass", drop_class)

    for name, (parent_name, row_name) in ENEMY_ARCHETYPES.items():
        parent_folder = "/Game/Blueprints/Characters"
        parent_path = asset_path(parent_folder, parent_name)
        bp = ensure_blueprint(name, parent_folder, parent_path)
        if not bp:
            continue
        cls = bp_class(parent_folder, name)
        if not cls:
            error("Missing generated class for %s" % name)
            continue
        cdo = unreal.get_default_object(cls)
        if not apply_enemy_stats(cdo, enemy_stats.get(row_name), drop_class, row_name == "Final Boss"):
            warn("No enemy data for %s (%s)" % (name, row_name))
        unreal.EditorAssetLibrary.save_asset(asset_path(parent_folder, name))

    # The reusable boss base gets the final-boss baseline.
    boss_cls = bp_class("/Game/Blueprints/Characters", "BP_BossBase")
    if boss_cls:
        boss_cdo = unreal.get_default_object(boss_cls)
        apply_enemy_stats(boss_cdo, enemy_stats.get("Final Boss"), drop_class, True)
        unreal.EditorAssetLibrary.save_asset(asset_path("/Game/Blueprints/Characters", "BP_BossBase"))

    # Give the Innocent Devil placeholder a visible body.
    devil_cls = bp_class("/Game/Blueprints/Characters", "BP_InnocentDevilActor")
    if devil_cls:
        devil_cdo = unreal.get_default_object(devil_cls)
        skeletal_cube = unreal.load_asset("/Engine/EngineMeshes/SkeletalCube.SkeletalCube")
        mesh = get_prop(devil_cdo, "Mesh")
        if skeletal_cube and mesh:
            set_prop(mesh, "SkeletalMeshAsset", skeletal_cube)
            set_prop(mesh, "RelativeScale3D", unreal.Vector(0.6, 0.6, 1.1))
        unreal.EditorAssetLibrary.save_asset(asset_path("/Game/Blueprints/Characters", "BP_InnocentDevilActor"))

    # Make dropped items visible in the blockout.
    item_cls = bp_class("/Game/Blueprints/World", "BP_ItemDrop")
    if item_cls:
        item_cdo = unreal.get_default_object(item_cls)
        cube = unreal.load_asset("/Engine/BasicShapes/Cube.Cube")
        item_mesh = get_prop(item_cdo, "ItemMesh")
        if cube and item_mesh:
            set_prop(item_mesh, "StaticMesh", cube)
            set_prop(item_mesh, "RelativeScale3D", unreal.Vector(0.25, 0.25, 0.25))
        unreal.EditorAssetLibrary.save_asset(asset_path("/Game/Blueprints/World", "BP_ItemDrop"))

    # Candles are the early source of forge materials.
    candle_cls = bp_class("/Game/Blueprints/World", "BP_CandleBreakable")
    if candle_cls:
        candle_cdo = unreal.get_default_object(candle_cls)
        candle_mesh = get_prop(candle_cdo, "CandleMesh")
        if cube and candle_mesh:
            set_prop(candle_mesh, "StaticMesh", cube)
            set_prop(candle_mesh, "RelativeScale3D", unreal.Vector(0.12, 0.12, 0.5))
        if item_cls:
            set_prop(candle_cdo, "ItemDropClass", item_cls)
        set_prop(candle_cdo, "PossibleDrops", ["Iron Shard", "Potion", "Silver Ingot"])
        set_prop(candle_cdo, "DropChance", 1.0)
        unreal.EditorAssetLibrary.save_asset(asset_path("/Game/Blueprints/World", "BP_CandleBreakable"))


def configure_character_blueprint(input_assets, imc):
    folder = "/Game/Blueprints/Characters"
    cls = bp_class(folder, "BP_HectorCharacter")
    if not cls:
        error("BP_HectorCharacter class not found")
        return

    cdo = unreal.get_default_object(cls)
    set_prop(cdo, "DefaultMappingContext", imc, required=True)
    for prop, asset_name in (
        ("MoveAction", "IA_Move"),
        ("LookAction", "IA_Look"),
        ("JumpAction", "IA_Jump"),
        ("LightAttackAction", "IA_LightAttack"),
        ("HeavyAttackAction", "IA_HeavyAttack"),
        ("GuardAction", "IA_Guard"),
        ("DodgeAction", "IA_Dodge"),
        ("InteractAction", "IA_Interact"),
        ("SummonDevilAction", "IA_SummonDevil"),
        ("CameraModeAction", "IA_CameraMode"),
        ("MapAction", "IA_Map"),
        ("PauseAction", "IA_Pause"),
        ("UseItemAction", "IA_UseItem"),
        ("ForgeAction", "IA_Forge"),
        ("QuickSaveAction", "IA_QuickSave"),
        ("QuickLoadAction", "IA_QuickLoad"),
    ):
        ia = input_assets.get(asset_name)
        if ia:
            set_prop(cdo, prop, ia, required=True)

    # Data-driven combat: point the component at the imported weapon table.
    combat = get_prop(cdo, "CombatComponent")
    weapon_table = unreal.load_asset("/Game/DataTables/DT_WeaponDataTable")
    if combat and weapon_table:
        set_prop(combat, "WeaponDataTableAsset", weapon_table, required=True)
        set_prop(combat, "DefaultWeaponName", "Short Sword")
    elif not combat:
        warn("BP_HectorCharacter has no CombatComponent default subobject")

    # Spawn the visible Innocent Devil actor when one is summoned.
    devil_component = get_prop(cdo, "InnocentDevilComponent")
    devil_class = bp_class("/Game/Blueprints/Characters", "BP_InnocentDevilActor")
    if devil_component and devil_class:
        set_prop(devil_component, "DevilActorClass", devil_class, required=True)
    elif not devil_component:
        warn("BP_HectorCharacter has no InnocentDevilComponent default subobject")

    # Placeholder silhouette so the knight is visible during the blockout.
    skeletal_cube = unreal.load_asset("/Engine/EngineMeshes/SkeletalCube.SkeletalCube")
    mesh = get_prop(cdo, "Mesh")
    if skeletal_cube and mesh:
        set_prop(mesh, "SkeletalMeshAsset", skeletal_cube)
        set_prop(mesh, "RelativeScale3D", unreal.Vector(0.9, 0.9, 1.8))

    unreal.EditorAssetLibrary.save_asset(asset_path(folder, "BP_HectorCharacter"))


def configure_game_mode_blueprint():
    core = "/Game/Blueprints/Core"
    gm_cls = bp_class(core, "BP_NobleArchimedesGameModeBase")
    hector_cls = bp_class("/Game/Blueprints/Characters", "BP_HectorCharacter")
    hud_cls = bp_class("/Game/Blueprints/UI", "BP_NobleArchimedesHUD")
    pc_cls = bp_class(core, "BP_NobleArchimedesPlayerController")

    if not (gm_cls and hector_cls and hud_cls and pc_cls):
        error("Cannot configure GameMode: missing generated classes")
        return

    cdo = unreal.get_default_object(gm_cls)
    set_prop(cdo, "DefaultPawnClass", hector_cls, required=True)
    set_prop(cdo, "PlayerControllerClass", pc_cls, required=True)
    set_prop(cdo, "HUDClass", hud_cls, required=True)

    # Give the HUD its default widget (the C++ layout for now).
    hud_widget_cls = bp_class("/Game/Blueprints/UI", "BP_NobleHUDWidget")
    if hud_widget_cls:
        hud_cdo = unreal.get_default_object(hud_cls)
        set_prop(hud_cdo, "HUDWidgetClass", hud_widget_cls, required=True)
        unreal.EditorAssetLibrary.save_asset(asset_path("/Game/Blueprints/UI", "BP_NobleArchimedesHUD"))
    else:
        warn("BP_NobleHUDWidget class unavailable; HUD will start empty")

    unreal.EditorAssetLibrary.save_asset(asset_path(core, "BP_NobleArchimedesGameModeBase"))


# ---------------------------------------------------------------------------
# Input
# ---------------------------------------------------------------------------

INPUT_ACTIONS = [
    ("IA_Move", unreal.InputActionValueType.AXIS2D),
    ("IA_Look", unreal.InputActionValueType.AXIS2D),
    ("IA_Jump", unreal.InputActionValueType.BOOLEAN),
    ("IA_LightAttack", unreal.InputActionValueType.BOOLEAN),
    ("IA_HeavyAttack", unreal.InputActionValueType.BOOLEAN),
    ("IA_Guard", unreal.InputActionValueType.BOOLEAN),
    ("IA_Dodge", unreal.InputActionValueType.BOOLEAN),
    ("IA_Interact", unreal.InputActionValueType.BOOLEAN),
    ("IA_SummonDevil", unreal.InputActionValueType.BOOLEAN),
    ("IA_CameraMode", unreal.InputActionValueType.BOOLEAN),
    ("IA_Map", unreal.InputActionValueType.BOOLEAN),
    ("IA_Pause", unreal.InputActionValueType.BOOLEAN),
    ("IA_UseItem", unreal.InputActionValueType.BOOLEAN),
    ("IA_Forge", unreal.InputActionValueType.BOOLEAN),
    ("IA_QuickSave", unreal.InputActionValueType.BOOLEAN),
    ("IA_QuickLoad", unreal.InputActionValueType.BOOLEAN),
]

# (action, key, negate X, negate Y, swizzle YXZ)
INPUT_MAPPINGS = [
    ("IA_Move", "W", False, False, True),
    ("IA_Move", "S", False, True, True),
    ("IA_Move", "D", False, False, False),
    ("IA_Move", "A", True, False, False),
    ("IA_Move", "Gamepad_Left2D", False, False, False),
    ("IA_Look", "Mouse2D", False, True, False),
    ("IA_Look", "Gamepad_Right2D", False, False, False),
    ("IA_Jump", "SpaceBar", False, False, False),
    ("IA_Jump", "Gamepad_FaceButton_Bottom", False, False, False),
    ("IA_LightAttack", "LeftMouseButton", False, False, False),
    ("IA_LightAttack", "Gamepad_FaceButton_Left", False, False, False),
    ("IA_HeavyAttack", "RightMouseButton", False, False, False),
    ("IA_HeavyAttack", "Gamepad_FaceButton_Top", False, False, False),
    ("IA_Guard", "LeftControl", False, False, False),
    ("IA_Guard", "Gamepad_LeftShoulder", False, False, False),
    ("IA_Dodge", "LeftShift", False, False, False),
    ("IA_Dodge", "Gamepad_FaceButton_Right", False, False, False),
    ("IA_Interact", "E", False, False, False),
    ("IA_Interact", "Gamepad_RightShoulder", False, False, False),
    ("IA_SummonDevil", "Q", False, False, False),
    ("IA_SummonDevil", "Gamepad_DPad_Up", False, False, False),
    ("IA_CameraMode", "C", False, False, False),
    ("IA_CameraMode", "Gamepad_DPad_Down", False, False, False),
    ("IA_Map", "Tab", False, False, False),
    ("IA_Map", "Gamepad_Special_Left", False, False, False),
    ("IA_Pause", "Escape", False, False, False),
    ("IA_Pause", "Gamepad_Special_Right", False, False, False),
    ("IA_UseItem", "R", False, False, False),
    ("IA_UseItem", "Gamepad_DPad_Left", False, False, False),
    ("IA_Forge", "F", False, False, False),
    ("IA_Forge", "Gamepad_DPad_Right", False, False, False),
    ("IA_QuickSave", "F5", False, False, False),
    ("IA_QuickLoad", "F9", False, False, False),
]


def create_input_assets():
    actions = {}
    for name, value_type in INPUT_ACTIONS:
        actions[name] = create_input_action(name, value_type)

    imc = create_mapping_context("IMC_Default")
    if not imc:
        return actions, None

    unreal.NobleInputBuilder.clear_mappings(imc)
    for action_name, key, neg_x, neg_y, swizzle in INPUT_MAPPINGS:
        action = actions.get(action_name)
        if not action:
            error("Missing input action %s for mapping %s" % (action_name, key))
            continue
        unreal.NobleInputBuilder.add_key_mapping(imc, action, key, neg_x, neg_y, swizzle)

    save_asset("/Game/Input/IMC_Default")
    return actions, imc


# ---------------------------------------------------------------------------
# Chapter 1 blockout
# ---------------------------------------------------------------------------

MAP_PATH = "/Game/Maps/Chap_01_AbandonedCastle"
BLOCKOUT_TAG = "NA_Blockout"


def clear_blockout():
    for actor in EAS.get_all_level_actors():
        if actor.actor_has_tag(BLOCKOUT_TAG) or isinstance(actor, unreal.PlayerStart):
            EAS.destroy_actor(actor)


def load_or_create_map():
    if not unreal.EditorAssetLibrary.does_asset_exist(MAP_PATH):
        error("Startup map missing: %s" % MAP_PATH)
        return False
    les = LES
    loaded = False
    try:
        loaded = les.load_level(MAP_PATH)
    except Exception as exc:
        warn("LevelEditorSubsystem.load_level failed: %r" % exc)
    if not loaded:
        try:
            loaded = unreal.EditorLoadingAndSavingUtils.load_map(MAP_PATH)
        except Exception as exc:
            error("Failed to load map: %r" % exc)
            return False
    return bool(loaded)


def spawn_box(label, center, size, cube, material):
    actor = EAS.spawn_actor_from_class(unreal.StaticMeshActor, center, unreal.Rotator(0, 0, 0))
    if not actor:
        error("Failed to spawn box %s" % label)
        return None
    actor.set_actor_label(label)
    actor.set_editor_property("tags", [BLOCKOUT_TAG])
    actor.set_actor_scale3d(unreal.Vector(size[0] / 100.0, size[1] / 100.0, size[2] / 100.0))
    comp = actor.get_component_by_class(unreal.StaticMeshComponent)
    if comp:
        comp.set_static_mesh(cube)
        if material:
            comp.set_material(0, material)
        comp.set_mobility(unreal.ComponentMobility.STATIC)
    return actor


def spawn_room(name, center, size, flags, enemy_classes, enemy_locations, bp_room):
    actor = EAS.spawn_actor_from_class(bp_room, center, unreal.Rotator(0, 0, 0))
    if not actor:
        error("Failed to spawn room %s" % name)
        return None
    actor.set_actor_label("Room_%s" % name.replace(" ", "_"))
    actor.set_editor_property("tags", [BLOCKOUT_TAG])
    set_prop(actor, "RoomName", name, required=True)
    set_prop(actor, "ChapterNumber", 1)
    for key, value in flags.items():
        if key == "Exits":
            continue
        set_prop(actor, key, value)
    set_prop(actor, "ExitRoomNames", flags.get("Exits", []))
    if enemy_classes:
        set_prop(actor, "EnemyClassesToSpawn", enemy_classes)
    if enemy_locations:
        set_prop(actor, "EnemySpawnLocations", enemy_locations)
    box = get_prop(actor, "RoomTriggerBox")
    if box:
        box.set_box_extent(unreal.Vector(size[0] * 0.5, size[1] * 0.5, 300.0), True)
    return actor


def build_room_shell(name, center, size, height, cube, material):
    cx, cy = center.x, center.y
    sx, sy = size[0], size[1]
    gap = 360.0
    thickness = 30.0

    spawn_box("Floor_%s" % name, unreal.Vector(cx, cy, -thickness * 0.5),
              (sx, sy, thickness), cube, material)

    half_seg = (sx - gap) * 0.25
    for sign in (-1.0, 1.0):
        # North / south walls (run along X)
        for x_sign in (-1.0, 1.0):
            spawn_box("WallNS_%s" % name,
                      unreal.Vector(cx + x_sign * (sx + gap) * 0.25, cy + sign * sy * 0.5, height * 0.5),
                      (half_seg * 2.0, thickness, height), cube, material)
        # East / west walls (run along Y)
        for y_sign in (-1.0, 1.0):
            spawn_box("WallEW_%s" % name,
                      unreal.Vector(cx + sign * sx * 0.5, cy + y_sign * (sy + gap) * 0.25, height * 0.5),
                      (thickness, half_seg * 2.0, height), cube, material)

    light = EAS.spawn_actor_from_class(unreal.PointLight, unreal.Vector(cx, cy, height - 50.0),
                                       unreal.Rotator(0, 0, 0))
    if light:
        light.set_actor_label("Light_%s" % name.replace(" ", "_"))
        light.set_editor_property("tags", [BLOCKOUT_TAG])
        comp = light.get_component_by_class(unreal.PointLightComponent)
        if comp:
            set_prop(comp, "Intensity", 6000.0)
            set_prop(comp, "AttenuationRadius", max(sx, sy) * 1.1)


def build_corridor(name, center, size, cube, material):
    spawn_box("Corridor_%s" % name, unreal.Vector(center[0], center[1], -15.0),
              (size[0], size[1], 30.0), cube, material)
    # center is a plain tuple here, so indexing is intentional.


def build_chapter_one():
    if not load_or_create_map():
        return

    clear_blockout()

    cube = unreal.load_asset("/Engine/BasicShapes/Cube.Cube")
    material = unreal.load_asset("/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial")
    bp_room = bp_class("/Game/Blueprints/World", "BP_Room")
    bp_enemy = bp_class("/Game/Blueprints/Characters", "BP_EnemyBase")
    bp_skeleton = bp_class("/Game/Blueprints/Characters", "BP_Skeleton")
    bp_zombie = bp_class("/Game/Blueprints/Characters", "BP_Zombie")
    bp_ghoul = bp_class("/Game/Blueprints/Characters", "BP_Ghoul")
    bp_boss = bp_class("/Game/Blueprints/Characters", "BP_SentinelKnight")

    if not (cube and bp_room and bp_enemy):
        error("Blockout prerequisites missing (cube=%r room=%r enemy=%r)" % (cube, bp_room, bp_enemy))
        return

    rooms = {
        "Entrance Hall": (unreal.Vector(0, 0, 0), (2200, 2200), 420),
        "Chapel": (unreal.Vector(0, 2800, 0), (1800, 1800), 520),
        "Save Room": (unreal.Vector(-2800, 0, 0), (900, 900), 320),
        "Boss Arena": (unreal.Vector(0, 5600, 0), (2800, 2800), 620),
    }

    for name, (center, size, height) in rooms.items():
        build_room_shell(name, center, size, height, cube, material)

    build_corridor("HallToChapel", (0, 1450), (620, 700), cube, material)
    build_corridor("HallToSave", (-1550, 0), (1700, 500), cube, material)
    build_corridor("ChapelToBoss", (0, 3750), (700, 500), cube, material)

    # Player start in the south of the Entrance Hall.
    start = EAS.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(0, -700, 120), unreal.Rotator(0, 90, 0))
    if start:
        start.set_actor_label("PlayerStart_Chap01")
        start.set_editor_property("tags", [BLOCKOUT_TAG])

    # Four Chapter 1 rooms with their enemy populations.
    spawn_room("Entrance Hall", rooms["Entrance Hall"][0], rooms["Entrance Hall"][1],
               {"bIsLocked": True, "bIsSaveRoom": False, "bIsBossArena": False,
                "Exits": ["Chapel", "Save Room"]},
               [bp_skeleton, bp_skeleton, bp_skeleton, bp_zombie, bp_zombie],
               [unreal.Vector(-600, 300, 100), unreal.Vector(-200, 500, 100),
                unreal.Vector(200, 500, 100), unreal.Vector(600, 300, 100),
                unreal.Vector(0, 700, 100)],
               bp_room)

    spawn_room("Chapel", rooms["Chapel"][0], rooms["Chapel"][1],
               {"bIsLocked": True, "bIsSaveRoom": False, "bIsBossArena": False,
                "Exits": ["Entrance Hall", "Boss Arena"]},
               [bp_ghoul, bp_ghoul],
               [unreal.Vector(-500, 2800, 100), unreal.Vector(500, 2800, 100)],
               bp_room)

    spawn_room("Save Room", rooms["Save Room"][0], rooms["Save Room"][1],
               {"bIsLocked": False, "bIsSaveRoom": True, "bIsBossArena": False,
                "Exits": ["Entrance Hall"]},
               [], [], bp_room)

    spawn_room("Boss Arena", rooms["Boss Arena"][0], rooms["Boss Arena"][1],
               {"bIsLocked": True, "bIsSaveRoom": False, "bIsBossArena": True,
                "Exits": ["Chapel"]},
               [bp_boss] if bp_boss else [bp_enemy],
               [unreal.Vector(0, 5900, 100)],
               bp_room)

    # Save room flame and a few pickups.
    bp_save = bp_class("/Game/Blueprints/World", "BP_SaveRoom")
    if bp_save:
        save_actor = EAS.spawn_actor_from_class(bp_save, unreal.Vector(-2800, 0, 60), unreal.Rotator(0, 0, 0))
        if save_actor:
            save_actor.set_actor_label("SaveRoom_Chap01")
            save_actor.set_editor_property("tags", [BLOCKOUT_TAG])
            set_prop(save_actor, "RoomName", "Save Room")
            set_prop(save_actor, "bIsSaveRoom", True)
            set_prop(save_actor, "bIsLocked", False)

    bp_item = bp_class("/Game/Blueprints/World", "BP_ItemDrop")
    if bp_item:
        for index, item in enumerate(("Potion", "Potion", "Potion",
                                      "Iron Shard", "Iron Shard", "Silver Ingot")):
            drop = EAS.spawn_actor_from_class(bp_item, unreal.Vector(400 + index * 150, -400, 80),
                                              unreal.Rotator(0, 0, 0))
            if drop:
                drop.set_actor_label("Item_%s_%d" % (item, index))
                drop.set_editor_property("tags", [BLOCKOUT_TAG])
                set_prop(drop, "ItemName", item)

    bp_candle = bp_class("/Game/Blueprints/World", "BP_CandleBreakable")
    if bp_candle:
        for index, location in enumerate(((-900, 900), (900, 900), (-900, -900), (900, -900))):
            candle = EAS.spawn_actor_from_class(bp_candle, unreal.Vector(location[0], location[1], 50),
                                                unreal.Rotator(0, 0, 0))
            if candle:
                candle.set_actor_label("Candle_%d" % index)
                candle.set_editor_property("tags", [BLOCKOUT_TAG])
                set_prop(candle, "PossibleDrops", ["Iron Shard", "Potion", "Silver Ingot"])
                set_prop(candle, "DropChance", 1.0)
                if bp_item:
                    set_prop(candle, "ItemDropClass", bp_item)

    # Directional light for global readability.
    sun = EAS.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 1500),
                                     unreal.Rotator(-50, -35, 0))
    if sun:
        sun.set_actor_label("Sun_Chap01")
        sun.set_editor_property("tags", [BLOCKOUT_TAG])
        comp = sun.get_component_by_class(unreal.DirectionalLightComponent)
        if comp:
            set_prop(comp, "Intensity", 4.0)

    try:
        if not LES.save_current_level():
            warn("save_current_level returned false")
    except Exception as exc:
        warn("save_current_level failed: %r" % exc)
        try:
            unreal.EditorLoadingAndSavingUtils.save_current_map()
        except Exception as exc2:
            error("Failed to save map: %r / %r" % (exc, exc2))

    log("Chapter 1 blockout rebuilt")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    log("Starting content build. Content dir: %s" % CONTENT_DIR)
    if not EAS or not LES:
        error("Editor subsystems unavailable; run this as a PythonScript commandlet with the editor modules loaded.")
        return

    import_all_data_tables()

    create_all_blueprints()

    actions, imc = create_input_assets()
    if imc:
        configure_character_blueprint(actions, imc)

    configure_game_mode_blueprint()
    build_chapter_one()

    unreal.EditorAssetLibrary.save_directory("/Game", only_if_is_dirty=False, recursive=True)

    log("SUMMARY created=%d updated=%d skipped=%d errors=%d" %
        (STATS["created"], STATS["updated"], STATS["skipped"], STATS["errors"]))
    for message in ERRORS:
        log("ERROR: " + message)


try:
    main()
except Exception:
    error("Unhandled exception:\n" + traceback.format_exc())
