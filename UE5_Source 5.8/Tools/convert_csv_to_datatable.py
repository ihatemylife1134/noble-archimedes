#!/usr/bin/env python3
"""
Convert CSV data tables to UE5 Data Table format.
Generates a .uasset-compatible JSON intermediate that can be used
as a reference when creating Data Tables in the UE5 Editor.
"""

import csv
import json
from pathlib import Path

DATA_TABLES_DIR = Path("UE5_Source/Content/DataTables")
OUTPUT_DIR = Path("UE5_Source/Content/DataTables/Converted")

CSV_TO_STRUCT = {
    "WeaponDataTable.csv": "FWeaponData",
    "MaterialDataTable.csv": "FMaterialData",
    "WeaponRecipeTable.csv": "FWeaponRecipe",
    "CompanionDataTable.csv": "FCompanionData",
    "EnemyDataTable.csv": "FEnemyData",
}


def csv_to_json(filename: str) -> dict:
    """Convert a CSV file to a JSON structure suitable for UE5 Data Table import."""
    filepath = DATA_TABLES_DIR / filename
    struct_name = CSV_TO_STRUCT.get(filename, "FTableRowBase")

    rows = {}
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Use first column as row name
            row_name = row.get(reader.fieldnames[0], "").strip()
            if not row_name:
                continue

            # Convert values to appropriate types
            row_data = {}
            for key, value in row.items():
                if not value or value.strip() == "":
                    continue

                # Try to convert to number
                try:
                    if "." in value:
                        row_data[key] = float(value)
                    else:
                        row_data[key] = int(value)
                except ValueError:
                    # Try boolean
                    if value.lower() in ("true", "false"):
                        row_data[key] = value.lower() == "true"
                    elif value.lower() in ("0", "1"):
                        row_data[key] = value.lower() == "1"
                    else:
                        row_data[key] = value

            rows[row_name] = row_data

    return {
        "StructName": struct_name,
        "SourceFile": filename,
        "RowCount": len(rows),
        "Rows": rows,
    }


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Converting CSV Data Tables to JSON...")
    print()

    for filename in CSV_TO_STRUCT:
        filepath = DATA_TABLES_DIR / filename
        if not filepath.exists():
            print(f"[SKIP] {filename} not found")
            continue

        result = csv_to_json(filename)
        output_file = OUTPUT_DIR / f"{filename.replace('.csv', '.json')}"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

        print(f"[OK] {filename} -> {output_file.name} ({result['RowCount']} rows)")

    print()
    print("Conversion complete. Use these JSON files as reference when")
    print("creating Data Tables in the UE5 Editor.")


if __name__ == "__main__":
    main()