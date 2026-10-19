# Data Tables — Import Instructions

These CSV files are designed to be imported into Unreal Engine 5 as Data Tables.

## Import Steps

1. In UE5 Editor, right-click in Content Browser
2. Select **Miscellaneous → Data Table**
3. Choose the appropriate Row Structure:
   - `WeaponDataTable.csv` → Row Structure: `FWeaponData`
   - `MaterialDataTable.csv` → Row Structure: `FMaterialData`
   - `WeaponRecipeTable.csv` → Row Structure: `FWeaponRecipe`
   - `InnocentDevilDataTable.csv` → Row Structure: `FInnocentDevilData`
   - `EnemyDataTable.csv` → Row Structure: `FEnemyData`
4. Name the Data Table (e.g., `DT_WeaponData`, `DT_MaterialData`, etc.)
5. The Data Table will be available in Blueprints and C++

## Row Structures

Create these C++ structs (already defined in `NobleArchimedesTypes.h`):
- `FWeaponData`
- `FMaterialData`
- `FWeaponRecipe`
- `FInnocentDevilData`
- `FEnemyData`

## Usage in Blueprints

- Get weapon data: `Get Data Table Row` → `DT_WeaponData` → Row Name: `"Short Sword"`
- Get Innocent Devil data: `Get Data Table Row` → `DT_InnocentDevilData` → Row Name: `"Fairy"`
- Check forge recipe: Iterate `DT_WeaponRecipe` and compare materials

## Example: Forge Logic

```
ForgeButton Clicked
├─ Get selected materials from inventory
├─ Call ForgeComponent.CombineWeapons(Materials, OutWeaponName)
├─ If Success:
│  ├─ Spawn weapon actor with OutWeaponName
│  ├─ Consume materials from inventory
│  └─ Play forge VFX/SFX
└─ If Failure:
  └─ Show "Missing Materials" message