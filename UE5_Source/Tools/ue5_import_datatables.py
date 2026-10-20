# UE5 Python Script: Import CSV Data Tables
# Run this in the UE5 Editor Python console:
#   exec(open(r"C:\Users\Madi\OneDrive\Documents\Default Project\noble-archimedes\UE5_Source\Tools\ue5_import_datatables.py").read())

import unreal
import os

# Data Table mappings: (CSV filename, Row Structure class name, Output asset name, Output folder)
datatable_mappings = [
    ("WeaponDataTable.csv", "FWeaponData", "DT_WeaponData", "/Game/DataTables"),
    ("MaterialDataTable.csv", "FMaterialData", "DT_MaterialData", "/Game/DataTables"),
    ("WeaponRecipeTable_Complete.csv", "FWeaponRecipe", "DT_WeaponRecipe", "/Game/DataTables"),
    ("InnocentDevilDataTable.csv", "FInnocentDevilData", "DT_InnocentDevilData", "/Game/DataTables"),
    ("EnemyDataTable.csv", "FEnemyData", "DT_EnemyData", "/Game/DataTables"),
    ("EnemyEncounterTable.csv", "FEnemyEncounter", "DT_EnemyEncounter", "/Game/DataTables"),
    ("ItemDropTable.csv", "FItemDropData", "DT_ItemDrop", "/Game/DataTables"),
    ("InnocentDevilEvolutionTable.csv", "FInnocentDevilEvolution", "DT_InnocentDevilEvolution", "/Game/DataTables"),
    ("WeaponMaterialRequirements.csv", "FWeaponMaterialRequirement", "DT_WeaponMaterialReq", "/Game/DataTables"),
    ("ChapterProgressionTable.csv", "FChapterProgression", "DT_ChapterProgression", "/Game/DataTables"),
    ("WeaponRecipeTable.csv", "FWeaponRecipe", "DT_WeaponRecipeBasic", "/Game/DataTables"),
]

CSV_DIR = r"C:\Users\Madi\OneDrive\Documents\Default Project\noble-archimedes\UE5_Source\Content\DataTables"
# Or use the project directory:
# CSV_DIR = r"C:\Projects\NobleArchimedes\Content\DataTables"

# Create output folder
unreal.EditorAssetLibrary.make_directory("/Game/DataTables")

# Import each CSV
imported = []
for csv_file, row_struct_name, asset_name, folder in datatable_mappings:
    asset_path = f"{folder}/{asset_name}"
    
    if unreal.EditorAssetLibrary.does_asset_exist(asset_path):
        print(f"[SKIP] {asset_path} already exists")
        continue
    
    # Find the row structure
    row_struct = unreal.load_class(None, f"/Script/NobleArchimedes.{row_struct_name}")
    if not row_struct:
        print(f"[ERROR] Could not find row struct: {row_struct_name}")
        continue
    
    # Create Data Table
    dt_factory = unreal.DataTableFactory()
    dt_factory.set_editor_property("Struct", row_struct)
    
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    new_dt = asset_tools.create_asset(asset_name, folder, unreal.DataTable, dt_factory)
    
    if new_dt:
        # Import CSV data
        csv_path = os.path.join(CSV_DIR, csv_file)
        if os.path.exists(csv_path):
            with open(csv_path, 'r', encoding='utf-8') as f:
                csv_data = f.read()
            new_dt.import_from_string(csv_data)
            unreal.EditorAssetLibrary.save_loaded_asset(new_dt)
            imported.append(asset_name)
            print(f"[OK] Imported {csv_file} → {asset_path} ({len(csv_data.splitlines())-1} rows)")
        else:
            print(f"[WARN] CSV file not found: {csv_path}")
    else:
        print(f"[ERROR] Failed to create Data Table: {asset_path}")

print(f"\nImported {len(imported)} Data Tables: {imported}")
print("=== Data Table import complete ===")