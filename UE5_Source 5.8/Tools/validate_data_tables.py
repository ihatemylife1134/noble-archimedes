#!/usr/bin/env python3
"""
Validate UE5 Data Table CSV files for consistency and completeness.
Run this before importing CSVs into UE5 to catch errors early.
"""

import csv
import sys
from pathlib import Path

DATA_TABLES_DIR = Path("UE5_Source/Content/DataTables")

REQUIRED_COLUMNS = {
    "WeaponDataTable.csv": ["WeaponName", "WeaponType", "AttackRange", "AttackSpeed", "BaseDamage", "DamageType", "EvoCrystalColor"],
    "MaterialDataTable.csv": ["MaterialName", "MaterialColorR", "MaterialColorG", "MaterialColorB", "IsRare", "Description"],
    "WeaponRecipeTable.csv": ["WeaponName", "WeaponType", "DamageType", "ForgeLevel", "RequiredMaterials"],
    "CompanionDataTable.csv": ["CompanionName", "CompanionType", "Level", "Experience", "Health", "MaxHealth", "Attack", "bIsUnlocked", "bIsEvolved", "EvolutionCrystalColor"],
    "EnemyDataTable.csv": ["EnemyName", "Chapter", "Health", "Damage", "AttackRange", "DetectionRange", "Weaknesses", "Tolerances", "ItemDrops", "CanBeStolen"],
}

VALID_WEAPON_TYPES = {"Sword", "Axe", "Spear", "Knuckles", "Special"}
VALID_DAMAGE_TYPES = {"Fire", "Ice", "Light", "Dark", "Poison", "Curse", "Paralyze", "Stone", "Slash", "Blunt", "Magic", "None"}
VALID_COMPANION_TYPES = {"Fairy", "Griffin", "Salamander", "Ogre", "Skeleton", "Witch", "Pumpkin", "None"}


def validate_csv(filename: str, required: list[str]) -> list[str]:
    """Validate a single CSV file. Returns list of error messages."""
    errors = []
    filepath = DATA_TABLES_DIR / filename

    if not filepath.exists():
        return [f"MISSING FILE: {filename}"]

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            header = reader.fieldnames or []

            # Check required columns
            missing = [c for c in required if c not in header]
            if missing:
                errors.append(f"  Missing columns: {', '.join(missing)}")

            for row_num, row in enumerate(reader, start=2):
                row_errors = []

                # Check for empty required fields
                for col in required:
                    if col in header and (not row.get(col) or row[col].strip() == ""):
                        row_errors.append(f"  Row {row_num}: Empty '{col}'")

                # Validate weapon type
                if filename == "WeaponDataTable.csv" and "WeaponType" in header:
                    wt = row.get("WeaponType", "").strip()
                    if wt and wt not in VALID_WEAPON_TYPES:
                        row_errors.append(f"  Row {row_num}: Invalid WeaponType '{wt}'")

                if filename == "WeaponRecipeTable.csv" and "WeaponType" in header:
                    wt = row.get("WeaponType", "").strip()
                    if wt and wt not in VALID_WEAPON_TYPES:
                        row_errors.append(f"  Row {row_num}: Invalid WeaponType '{wt}'")

                # Validate damage type
                if "DamageType" in header:
                    dt = row.get("DamageType", "").strip()
                    if dt and dt not in VALID_DAMAGE_TYPES:
                        row_errors.append(f"  Row {row_num}: Invalid DamageType '{dt}'")

                # Validate companion type
                if filename == "CompanionDataTable.csv" and "CompanionType" in header:
                    ct = row.get("CompanionType", "").strip()
                    if ct and ct not in VALID_COMPANION_TYPES:
                        row_errors.append(f"  Row {row_num}: Invalid CompanionType '{ct}'")

                # Validate numeric fields
                numeric_fields = ["AttackRange", "AttackSpeed", "BaseDamage", "Health", "MaxHealth", "Attack",
                                  "Level", "Experience", "ForgeLevel", "MaterialColorR", "MaterialColorG",
                                  "MaterialColorB", "DetectionRange"]
                for col in numeric_fields:
                    if col in header:
                        val = row.get(col, "").strip()
                        if val:
                            try:
                                float(val)
                            except ValueError:
                                row_errors.append(f"  Row {row_num}: Invalid number in '{col}': '{val}'")

                # Validate boolean fields
                bool_fields = ["IsRare", "bIsUnlocked", "bIsEvolved", "CanBeStolen"]
                for col in bool_fields:
                    if col in header:
                        val = row.get(col, "").strip().lower()
                        if val and val not in ("true", "false", "0", "1"):
                            row_errors.append(f"  Row {row_num}: Invalid boolean in '{col}': '{val}'")

                errors.extend(row_errors)

    except Exception as e:
        errors.append(f"  ERROR reading file: {e}")

    return errors


def main():
    print("Validating UE5 Data Table CSV files...")
    print(f"Directory: {DATA_TABLES_DIR.absolute()}")
    print()

    total_errors = 0

    for filename, required in REQUIRED_COLUMNS.items():
        errors = validate_csv(filename, required)
        if errors:
            print(f"[{filename}]")
            for err in errors:
                print(f"  {err}")
            total_errors += len(errors)
        else:
            print(f"[{filename}] OK")

    print()
    if total_errors == 0:
        print("All CSV files valid! Ready for UE5 import.")
        return 0
    else:
        print(f"Found {total_errors} error(s). Fix before importing into UE5.")
        return 1


if __name__ == "__main__":
    sys.exit(main())