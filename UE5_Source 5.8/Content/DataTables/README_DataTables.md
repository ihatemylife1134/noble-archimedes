# Data Tables — Import Instructions

These CSV files are designed to be imported into Unreal Engine 5 as Data Tables.

## Import Steps

1. In UE5 Editor, right-click in Content Browser
2. Select **Miscellaneous → Data Table**
3. Choose the appropriate Row Structure:
   - `WeaponDataTable.csv` → Row Structure: `FWeaponData`
   - `MaterialDataTable.csv` → Row Structure: `FMaterialData`
   - `WeaponRecipeTable.csv` / `WeaponRecipeTable_Complete.csv` → Row Structure: `FWeaponRecipe`
   - `WeaponMaterialRequirements.csv` → Custom material requirement struct
   - `InnocentDevilDataTable.csv` → Row Structure: `FInnocentDevilData`
   - `EnemyDataTable.csv` → Row Structure: `FEnemyData`
   - `EnemyEncounterTable.csv` → Custom encounter struct
   - `ItemDropTable.csv` → Custom item drop struct
   - `InnocentDevilEvolutionTable.csv` → Custom evolution struct
   - `ChapterProgressionTable.csv` → Custom chapter struct
4. Name the Data Table (e.g., `DT_WeaponData`, `DT_MaterialData`, etc.)
5. The Data Table will be available in Blueprints and C++

## Row Structures

Create these C++ structs (already defined in `NobleArchimedesTypes.h`):
- `FWeaponData`
- `FMaterialData`
- `FWeaponRecipe`
- `FInnocentDevilData`
- `FEnemyData`

Additional structs to create for encounter/drop/evolution data:
- `FEnemyEncounter` (Chapter, EnemyName, Count, SpawnLocation, RespawnTime, IsBoss, Stealable, StealItem, Weakness, Tolerance, Health, Damage)
- `FItemDropData` (EnemyName, ItemName, DropChance, IsStealOnly, IsRare)
- `FWeaponMaterialRequirement` (WeaponName, Material1-4, Material1-4Count)
- `FInnocentDevilEvolution` (DevilName, DevilType, Level, BaseForm, EvolvedForm, FinalForm, EvoCrystalRequired, EvoCrystalCount, AbilityUnlock)
- `FChapterProgression` (Chapter, ChapterName, UnlockRequirement, SaveRooms, GreenDoorRooms, InnocentDevilAcquired, WeaponUnlocked, AreaType)

## Validation

Run `"UE5_Source 5.8/Tools/validate_rebuild_fidelity.py"` to verify all data tables
match the original Castlevania: Curse of Darkness design before importing.

## Conversion

Run `"UE5_Source 5.8/Tools/convert_csv_to_datatable.py"` to generate JSON reference
files for Data Table creation in the UE5 Editor.

## Asset Naming

See `../Blueprints/AssetNamingSpec.md` for the complete naming convention.

---

**All data is original research based on the Bradygames Official Strategy Guide
and PS2 disc structure analysis. No copyrighted game data was extracted.**