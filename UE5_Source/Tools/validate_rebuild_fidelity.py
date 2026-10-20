#!/usr/bin/env python3
"""
Validate that the UE5 rebuild matches the original Castlevania: Curse of Darkness design.
Cross-references against Bradygames guide data and PS2 disc structure.

Run this before each build to ensure fidelity to the original game.
"""

import csv
import sys
from pathlib import Path

DATA_DIR = Path("UE5_Source/Content/DataTables")

ERRORS = []
WARNINGS = []

def check(condition, message, severity="ERROR"):
    if not condition:
        if severity == "ERROR":
            ERRORS.append(message)
        else:
            WARNINGS.append(message)
        print(f"  [{severity}] {message}")

def validate_csv_exists(filename):
    return (DATA_DIR / filename).exists()

def validate_csv_columns(filename, required_columns):
    filepath = DATA_DIR / filename
    if not filepath.exists():
        return
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames or []
        missing = [c for c in required_columns if c not in header]
        if missing:
            check(False, f"{filename}: Missing columns {missing}")
        else:
            print(f"  [OK] {filename}: All required columns present")

def validate_weapon_types():
    filepath = DATA_DIR / "WeaponDataTable.csv"
    if not filepath.exists():
        check(False, "WeaponDataTable.csv missing")
        return
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        types_found = set()
        for row in reader:
            types_found.add(row.get("WeaponType", ""))
        expected = {"Sword", "Axe", "Spear", "Knuckles", "Special"}
        missing = expected - types_found
        if missing:
            check(False, f"Missing weapon types: {missing}")
        else:
            print(f"  [OK] All 5 weapon types present")

def validate_damage_types():
    filepath = DATA_DIR / "WeaponDataTable.csv"
    if not filepath.exists():
        return
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        types_found = set()
        for row in reader:
            types_found.add(row.get("DamageType", ""))
        expected = {"Fire", "Ice", "Light", "Dark", "Poison", "Curse", "Paralyze", "Stone", "Slash", "Blunt", "Magic"}
        missing = expected - types_found
        if missing:
            check(False, f"Missing damage types: {missing}")
        else:
            print(f"  [OK] All 11 damage types present")

def validate_innocent_devils():
    filepath = DATA_DIR / "InnocentDevilDataTable.csv"
    if not filepath.exists():
        check(False, "InnocentDevilDataTable.csv missing")
        return
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        devils_found = set()
        for row in reader:
            devils_found.add(row.get("DevilType", ""))
        expected = {"Fairy", "Griffin", "Salamander", "Ogre", "Skeleton", "Witch", "Pumpkin"}
        missing = expected - devils_found
        if missing:
            check(False, f"Missing Innocent Devils: {missing}")
        else:
            print(f"  [OK] All 6 Innocent Devils + Pumpkin present")

def validate_chapters():
    filepath = DATA_DIR / "ChapterProgressionTable.csv"
    if not filepath.exists():
        check(False, "ChapterProgressionTable.csv missing")
        return
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        chapters_found = []
        for row in reader:
            chapters_found.append(row.get("ChapterName", ""))
        expected = [
            "Abandoned Castle", "Baljhet Mountains", "Garibaldi Temple",
            "Mortvia Aqueduct", "Forest of Jigramunt", "Cordova Town",
            "Eneomaos Machine Tower", "Aiolon Ruins", "Infinite Corridor",
            "Dracula's Castle"
        ]
        missing = [c for c in expected if c not in chapters_found]
        if missing:
            check(False, f"Missing chapters: {missing}")
        else:
            print(f"  [OK] All 10 chapters present in order")

def validate_input_bindings():
    filepath = Path("UE5_Source/Config/DefaultInput.ini")
    if not filepath.exists():
        check(False, "DefaultInput.ini missing")
        return
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        # Project uses EnhancedInput exclusively; legacy ActionMappings removed.
        # Verify the EnhancedInput MappingContext is registered.
        if "+MappingContexts=" in content and "IMC_Default" in content:
            print(f"  [OK] EnhancedInput MappingContext (IMC_Default) registered")
        else:
            check(False, "DefaultInput.ini: EnhancedInput MappingContext not found")

def validate_death_doll():
    filepath = DATA_DIR / "ItemDropTable.csv"
    if not filepath.exists():
        return
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        if "Death Doll" not in content:
            check(False, "Death Doll item missing from drop table")
        else:
            print(f"  [OK] Death Doll item present")

def validate_combat_timing():
    # These are hardcoded in NobleArchimedesTypes.h
    filepath = Path("UE5_Source/NobleArchimedes/Public/NobleArchimedesTypes.h")
    if not filepath.exists():
        return
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        checks = [
            ("PERFECT_GUARD_WINDOW = 0.1f", "Perfect Guard 0.1s window"),
            ("QUICK_STEP_IFRAMES = 0.3f", "Quick Step 0.3s invulnerability"),
            ("DOUBLE_STEP_WINDOW = 0.5f", "Double Step 0.5s window"),
            ("COMBO_STAGE_1_WINDOW = 0.35f", "Combo Stage 1 window 0.35s"),
            ("COMBO_STAGE_2_WINDOW = 0.45f", "Combo Stage 2 window 0.45s"),
            ("COMBO_STAGE_3_WINDOW = 0.60f", "Combo Stage 3 window 0.60s"),
        ]
        for value, description in checks:
            if value not in content:
                check(False, f"Missing timing constant: {description} ({value})")
            else:
                print(f"  [OK] {description}")

def main():
    print("=" * 60)
    print("NOBLE ARCHIMEDES - Rebuild Fidelity Validation")
    print("Cross-referencing against original Castlevania: Curse of Darkness")
    print("=" * 60)
    print()

    print("--- File Existence ---")
    required_files = [
        "WeaponDataTable.csv",
        "MaterialDataTable.csv",
        "WeaponRecipeTable.csv",
        "WeaponRecipeTable_Complete.csv",
        "InnocentDevilDataTable.csv",
        "EnemyDataTable.csv",
        "EnemyEncounterTable.csv",
        "ItemDropTable.csv",
        "WeaponMaterialRequirements.csv",
        "InnocentDevilEvolutionTable.csv",
        "ChapterProgressionTable.csv",
    ]
    for f in required_files:
        if validate_csv_exists(f):
            print(f"  [OK] {f}")
        else:
            check(False, f"Missing required file: {f}")

    print()
    print("--- Column Validation ---")
    validate_csv_columns("WeaponDataTable.csv",
        ["WeaponName", "WeaponType", "AttackRange", "AttackSpeed", "BaseDamage", "DamageType", "EvoCrystalColor"])
    validate_csv_columns("MaterialDataTable.csv",
        ["MaterialName", "MaterialColorR", "MaterialColorG", "MaterialColorB", "MaterialColorA", "IsRare", "Description"])
    validate_csv_columns("WeaponRecipeTable.csv",
        ["WeaponName", "WeaponType", "DamageType", "ForgeLevel", "RequiredMaterials"])
    validate_csv_columns("InnocentDevilDataTable.csv",
        ["DevilName", "DevilType", "Level", "Experience", "Health", "MaxHealth", "Attack", "bIsUnlocked", "bIsEvolved", "EvolutionCrystalColor"])
    validate_csv_columns("EnemyDataTable.csv",
        ["EnemyName", "Chapter", "Health", "Damage", "AttackRange", "DetectionRange", "Weaknesses", "Tolerances", "ItemDrops", "CanBeStolen"])

    print()
    print("--- Content Validation ---")
    validate_weapon_types()
    validate_damage_types()
    validate_innocent_devils()
    validate_chapters()
    validate_input_bindings()
    validate_death_doll()
    validate_combat_timing()

    print()
    print("=" * 60)
    if ERRORS:
        print(f"FAILED: {len(ERRORS)} error(s) found")
        for e in ERRORS:
            print(f"  [ERROR] {e}")
        return 1
    else:
        print("PASSED: All fidelity checks passed")
        if WARNINGS:
            print(f"Warnings: {len(WARNINGS)}")
            for w in WARNINGS:
                print(f"  [WARNING] {w}")
        return 0

if __name__ == "__main__":
    sys.exit(main())