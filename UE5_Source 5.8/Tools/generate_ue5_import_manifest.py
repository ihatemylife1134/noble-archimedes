#!/usr/bin/env python3
"""
Generate a UE5 import manifest for all data tables and assets.
This creates a JSON manifest that can be used to track what needs
to be imported into the UE5 Editor.
"""

import csv
import json
from pathlib import Path

DATA_DIR = Path("UE5_Source 5.8/Content/DataTables")
OUTPUT_FILE = Path("UE5_Source 5.8/Content/DataTables/ImportManifest.json")

# Map CSV files to their UE5 Data Table row structures
CSV_TO_STRUCT = {
    "WeaponDataTable.csv": "FWeaponData",
    "MaterialDataTable.csv": "FMaterialData",
    "WeaponRecipeTable.csv": "FWeaponRecipe",
    "WeaponRecipeTable_Complete.csv": "FWeaponRecipe",
    "WeaponMaterialRequirements.csv": "FWeaponMaterialRequirement",
    "InnocentDevilDataTable.csv": "FInnocentDevilData",
    "EnemyDataTable.csv": "FEnemyData",
    "EnemyEncounterTable.csv": "FEnemyEncounter",
    "ItemDropTable.csv": "FItemDrop",
    "InnocentDevilEvolutionTable.csv": "FInnocentDevilEvolution",
    "ChapterProgressionTable.csv": "FChapterProgression",
}

def count_rows(filepath):
    """Count data rows in a CSV file (excluding header)."""
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        return sum(1 for _ in reader)

def main():
    manifest = {
        "format": "UE5 Data Table Import Manifest",
        "version": "1.0",
        "total_tables": 0,
        "tables": []
    }

    for csv_file, struct_name in CSV_TO_STRUCT.items():
        filepath = DATA_DIR / csv_file
        if not filepath.exists():
            print(f"[SKIP] {csv_file} not found")
            continue

        row_count = count_rows(filepath)
        table_entry = {
            "csv_file": csv_file,
            "struct_name": struct_name,
            "suggested_name": f"DT_{csv_file.replace('.csv', '')}",
            "row_count": row_count,
            "status": "pending_import"
        }
        manifest["tables"].append(table_entry)
        manifest["total_tables"] += 1
        print(f"  [OK] {csv_file}: {row_count} rows → {struct_name}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print()
    print(f"Manifest written to {OUTPUT_FILE}")
    print(f"Total tables: {manifest['total_tables']}")

if __name__ == "__main__":
    main()