#!/usr/bin/env python3
"""
Validate the UE5 Data Table CSV sources and the import manifest.

Run from the repository root:
    python UE5_Source 5.8/Tools/validate_data_tables.py

Checks:
  * required files and columns
  * consistent field counts on every row
  * required key fields are populated
  * numeric / boolean / enum fields parse
  * manifest row counts and asset names match the CSVs
  * weapon recipe coverage matches the weapon list
"""

import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA_TABLES_DIR = HERE.parent / "Content" / "DataTables"
if not DATA_TABLES_DIR.exists():
    DATA_TABLES_DIR = Path("UE5_Source 5.8/Content/DataTables")

ERRORS = []
WARNINGS = []


def error(message):
    ERRORS.append(message)


def warn(message):
    WARNINGS.append(message)


SCHEMAS = {
    "WeaponDataTable.csv": [
        "WeaponName", "WeaponType", "AttackRange", "AttackSpeed", "BaseDamage",
        "DamageType", "EvoCrystalColor", "ComboAnimCount", "FinalAttackAnimCount",
    ],
    "MaterialDataTable.csv": [
        "MaterialName", "MaterialColorR", "MaterialColorG", "MaterialColorB",
        "MaterialColorA", "IsRare", "Description",
    ],
    "WeaponRecipeTable.csv": [
        "WeaponName", "WeaponType", "DamageType", "ForgeLevel", "RequiredMaterials",
    ],
    "WeaponRecipeTable_Complete.csv": [
        "WeaponName", "WeaponType", "DamageType", "ForgeLevel", "RequiredMaterials",
        "AttackPower", "AttackSpeed", "AttackRange", "EvoCrystalColor",
    ],
    "WeaponMaterialRequirements.csv": [
        "WeaponName", "Material1", "Material1Count", "Material2", "Material2Count",
        "Material3", "Material3Count", "Material4", "Material4Count",
    ],
    "InnocentDevilDataTable.csv": [
        "DevilName", "DevilType", "Level", "Experience", "Health", "MaxHealth",
        "Attack", "bIsUnlocked", "bIsEvolved", "EvolutionCrystalColor",
    ],
    "EnemyDataTable.csv": [
        "EnemyName", "Chapter", "Health", "Damage", "AttackRange", "DetectionRange",
        "Weaknesses", "Tolerances", "ItemDrops", "CanBeStolen",
    ],
    "EnemyEncounterTable.csv": [
        "Chapter", "EnemyName", "Count", "SpawnLocation", "RespawnTime", "IsBoss",
        "Stealable", "StealItem", "Weakness", "Tolerance", "Health", "Damage",
    ],
    "ItemDropTable.csv": [
        "EnemyName", "ItemName", "DropChance", "IsStealOnly", "IsRare",
    ],
    "InnocentDevilEvolutionTable.csv": [
        "DevilName", "DevilType", "Level", "BaseForm", "EvolvedForm", "FinalForm",
        "EvoCrystalRequired", "EvoCrystalCount", "AbilityUnlock",
    ],
    "ChapterProgressionTable.csv": [
        "Chapter", "ChapterName", "UnlockRequirement", "SaveRooms", "GreenDoorRooms",
        "InnocentDevilAcquired", "WeaponUnlocked", "AreaType",
    ],
}

KEY_FIELDS = {
    "WeaponDataTable.csv": ["WeaponName"],
    "MaterialDataTable.csv": ["MaterialName"],
    "WeaponRecipeTable.csv": ["WeaponName"],
    "WeaponRecipeTable_Complete.csv": ["WeaponName"],
    "WeaponMaterialRequirements.csv": ["WeaponName"],
    "InnocentDevilDataTable.csv": ["DevilName"],
    "EnemyDataTable.csv": ["EnemyName"],
    "EnemyEncounterTable.csv": ["Chapter", "EnemyName"],
    "ItemDropTable.csv": ["EnemyName", "ItemName"],
    "InnocentDevilEvolutionTable.csv": ["DevilName", "Level"],
    "ChapterProgressionTable.csv": ["Chapter"],
}

INT_FIELDS = {
    "Chapter", "Count", "Level", "Experience", "Health", "MaxHealth", "Attack",
    "ForgeLevel", "EvoCrystalCount", "Material1Count", "Material2Count",
    "Material3Count", "Material4Count", "ComboAnimCount", "FinalAttackAnimCount",
    "SaveRooms", "GreenDoorRooms",
}

FLOAT_FIELDS = {
    "AttackRange", "AttackSpeed", "BaseDamage", "Damage", "DetectionRange",
    "RespawnTime", "DropChance", "AttackPower", "MaterialColorR",
    "MaterialColorG", "MaterialColorB", "MaterialColorA",
}

BOOL_FIELDS = {
    "IsRare", "bIsRare", "bIsUnlocked", "bIsEvolved", "CanBeStolen", "IsBoss",
    "Stealable", "IsStealOnly",
}

WEAPON_TYPES = {"Sword", "Axe", "Spear", "Knuckles", "Special"}
DAMAGE_TYPES = {
    "Fire", "Ice", "Light", "Dark", "Poison", "Curse", "Paralyze", "Stone",
    "Slash", "Blunt", "Magic",
}
WEAPON_CRYSTAL_COLORS = {"Light", "Dark", "Fire", "Ice", "None"}
DEVIL_CRYSTAL_COLORS = WEAPON_CRYSTAL_COLORS | {"Slash", "Magic", "Special"}
DEVIL_TYPES = {
    "Fairy", "Griffin", "Salamander", "Ogre", "Skeleton", "Witch", "Pumpkin",
    "None",
}

ENUM_FIELDS = {
    "WeaponType": WEAPON_TYPES,
    "DamageType": DAMAGE_TYPES,
    "EvoCrystalColor": WEAPON_CRYSTAL_COLORS,
    "EvolutionCrystalColor": DEVIL_CRYSTAL_COLORS,
    "DevilType": DEVIL_TYPES,
}


def read_csv(path):
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.reader(handle))


def validate_file(name, schema):
    path = DATA_TABLES_DIR / name
    if not path.exists():
        error("missing file: %s" % name)
        return None

    rows = read_csv(path)
    if not rows:
        error("%s is empty" % name)
        return None

    header = [column.strip() for column in rows[0]]
    if header != schema:
        error("%s header mismatch\n    expected: %s\n    actual:   %s" %
              (name, schema, header))
        return None

    data = rows[1:]
    for index, row in enumerate(data, start=2):
        if len(row) != len(header):
            error("%s line %d: %d fields, expected %d" %
                  (name, index, len(row), len(header)))
            continue

        record = {header[i]: row[i].strip() for i in range(len(header))}

        for field in KEY_FIELDS[name]:
            if not record.get(field):
                error("%s line %d: empty key field %s" % (name, index, field))

        for field in INT_FIELDS.intersection(header):
            value = record.get(field, "")
            if value == "":
                continue
            try:
                int(float(value))
            except ValueError:
                error("%s line %d: %s is not an integer: %r" %
                      (name, index, field, value))

        for field in FLOAT_FIELDS.intersection(header):
            value = record.get(field, "")
            if value == "":
                continue
            try:
                number = float(value)
            except ValueError:
                error("%s line %d: %s is not a number: %r" %
                      (name, index, field, value))
                continue
            if not (0.0 <= number <= 1.0) and "Color" in field:
                error("%s line %d: %s is outside 0..1: %r" %
                      (name, index, field, value))

        for field in BOOL_FIELDS.intersection(header):
            value = record.get(field, "")
            if value and value.lower() not in {"true", "false", "0", "1"}:
                error("%s line %d: %s is not a boolean: %r" %
                      (name, index, field, value))

        for field, allowed in ENUM_FIELDS.items():
            if field not in header:
                continue
            value = record.get(field, "")
            if value and value not in allowed:
                error("%s line %d: %s has unknown value %r" %
                      (name, index, field, value))

    print("[%s] OK (%d rows)" % (name, len(data)))
    return data


def validate_manifest():
    path = DATA_TABLES_DIR / "ImportManifest.json"
    if not path.exists():
        error("missing ImportManifest.json")
        return

    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        error("ImportManifest.json is not valid JSON: %r" % exc)
        return

    tables = manifest.get("tables", [])
    if manifest.get("total_tables") != len(tables):
        error("manifest total_tables=%r but has %d entries" %
              (manifest.get("total_tables"), len(tables)))

    seen_assets = set()
    manifest_files = set()
    for entry in tables:
        csv_file = entry.get("csv_file", "")
        manifest_files.add(csv_file)
        csv_path = DATA_TABLES_DIR / csv_file
        if not csv_path.exists():
            error("manifest references missing CSV: %s" % csv_file)
            continue

        rows = read_csv(csv_path)
        expected = int(entry.get("row_count", -1))
        actual = max(0, len(rows) - 1)
        if expected != actual:
            error("%s manifest row_count=%d, CSV has %d" %
                  (csv_file, expected, actual))

        struct_name = entry.get("struct_name", "")
        if not struct_name.startswith("F"):
            error("%s struct_name should start with F: %r" % (csv_file, struct_name))

        asset_name = entry.get("suggested_name", "")
        if not asset_name.startswith("DT_"):
            error("%s suggested_name should start with DT_: %r" % (csv_file, asset_name))
        if asset_name in seen_assets:
            error("duplicate suggested_name: %s" % asset_name)
        seen_assets.add(asset_name)

    csv_files = {path.name for path in DATA_TABLES_DIR.glob("*.csv")}
    missing_entries = csv_files - manifest_files
    if missing_entries:
        error("CSVs missing from manifest: %s" % ", ".join(sorted(missing_entries)))

    print("[ImportManifest.json] OK (%d tables)" % len(tables))


def validate_cross_table():
    weapons_path = DATA_TABLES_DIR / "WeaponDataTable.csv"
    recipe_path = DATA_TABLES_DIR / "WeaponRecipeTable.csv"
    if not (weapons_path.exists() and recipe_path.exists()):
        return

    weapons = read_csv(weapons_path)
    recipes = read_csv(recipe_path)
    weapon_names = [row[0].strip() for row in weapons[1:] if row]
    recipe_names = [row[0].strip() for row in recipes[1:] if row]

    missing = [name for name in weapon_names if name not in recipe_names]
    if missing:
        error("WeaponRecipeTable.csv is missing recipes for: %s" % ", ".join(missing))

    extra = [name for name in recipe_names if name not in weapon_names]
    if extra:
        error("WeaponRecipeTable.csv has unknown weapons: %s" % ", ".join(extra))

    if len(set(weapon_names)) != len(weapon_names):
        error("WeaponDataTable.csv has duplicate weapon names")

    # Chapter progression should list chapters 1..10 exactly once.
    chapter_path = DATA_TABLES_DIR / "ChapterProgressionTable.csv"
    if chapter_path.exists():
        chapters = read_csv(chapter_path)
        numbers = []
        for row in chapters[1:]:
            if row:
                try:
                    numbers.append(int(row[0]))
                except ValueError:
                    error("ChapterProgressionTable.csv has a non-integer chapter: %r" % row[0])
        if sorted(numbers) != list(range(1, 11)):
            error("ChapterProgressionTable.csv must contain chapters 1..10 exactly once")

    print("[cross-table] OK")


def main():
    if not DATA_TABLES_DIR.exists():
        error("data table directory not found: %s" % DATA_TABLES_DIR)
    else:
        for name, schema in SCHEMAS.items():
            validate_file(name, schema)
        validate_manifest()
        validate_cross_table()

    print()
    if WARNINGS:
        print("Warnings:")
        for message in WARNINGS:
            print("  WARNING: " + message)
    if ERRORS:
        print("Found %d error(s):" % len(ERRORS))
        for message in ERRORS:
            print("  ERROR: " + message)
        return 1

    print("PASSED: data tables are consistent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
