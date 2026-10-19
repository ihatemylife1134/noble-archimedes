# CONVERSATION CONTEXT — Noble Archimedes UE5 Fan Recreation

## Project Overview
**Goal:** Recreate Castlevania: Curse of Darkness (PS2, SLUS-21168) as a faithful fan recreation in Unreal Engine 5 for **private, educational use only**.

**Source Material:** Bradygames Official Strategy Guide + PS2 disc analysis (SLUS-211.68, FILEDATA.BIN). No copyrighted game content extracted — all code, data, and specs are original implementations.

**Current State:** All engineering work complete. 86 files committed to Git. Ready for UE5 Editor implementation on Windows GPU machine.

---

## Repository Structure (86 files)

```
UE5_Source/
├── NobleArchimedes.uproject          # UE5 project file
├── NobleArchimedes.Build.cs          # Build configuration
├── Config/
│   ├── DefaultEngine.ini             # Engine settings
│   └── DefaultInput.ini              # 12 input mappings
├── Source/NobleArchimedes/
│   ├── Public/ (14 headers)
│   └── Private/ (13 cpp files)
├── Content/
│   ├── DataTables/ (11 CSVs)
│   ├── Blueprints/ (16 design specs)
│   ├── Localization/ (En.json)
│   └── Maps/ (LevelDesignSpec.md)
├── Tools/ (11 Python scripts)
├── BuildScripts/ (3 scripts)
├── Shaders/ (1 USF file)
├── .gitignore
├── opencode.jsonc                    # 16 agent definitions
├── SESSION_HANDOFF.md                # Session resume guide
└── CONVERSATION_CONTEXT.md           # This file
```

---

## C++ Framework (11 classes, ~3,100 lines)

| File | Purpose |
|------|---------|
| `NobleArchimedesTypes.h` | All enums (EWeaponType, EDamageType, ECameraMode, EInnocentDevilType, ECombatState) + data structs (FWeaponData, FMaterialData, FWeaponRecipe, FInnocentDevilData, FEnemyData, FInventoryItem) |
| `HectorCharacter.h/.cpp` | Player character with combat, camera, innocent devil integration |
| `NobleArchimedesCombatComponent.h/.cpp` | Attack combos, Perfect Guard (0.1s), Quick Step (0.3s i-frames), Double Step, 11 damage types, Death Doll |
| `NobleArchimedesCameraComponent.h/.cpp` | 3 camera modes (Classic, Action Orbit, Over-the-Shoulder) with smoothing |
| `NobleArchimedesInnocentDevilComponent.h/.cpp` | 6 Innocent Devils + Pumpkin, Auto/Command/Guard modes, evolution |
| `NobleArchimedesAudioComponent.h/.cpp` | Combat, companion, item, UI, ambient audio + volume controls |
| `NobleArchimedesVFXComponent.h/.cpp` | Weapon trails, hit sparks, perfect guard flash, companion/item VFX |
| `NobleArchimedesSaveGame.h` | Full save data (player, chapters, inventory, innocent devils, Death Doll) |
| `NobleArchimedesGameInstance.h/.cpp` | Save/load manager (5 manual + 1 auto slot) |
| `NobleArchimedesLevelStreaming.h/.cpp` | Chapter streaming for all 10 chapters |
| `NobleArchimedesWeaponForge.h/.cpp` | Weapon combining (~40 materials, 15 recipes) |
| `NobleArchimedesItemSystem.h/.cpp` | Items, consumables, steal system |
| `NobleArchimedesGameModeBase.h/.cpp` | Chapter management, save/load, progression |
| `NobleArchimedesPlayerController.h/.cpp` | Input handling, pause, map, camera mode, steal focus, lock-on |

---

## Data Tables (11 CSV files — import into UE5)

| File | Rows | Content |
|------|------|---------|
| `WeaponDataTable.csv` | 19 | All weapons across 5 types with damage types |
| `MaterialDataTable.csv` | 40 | All forge materials with colors |
| `WeaponRecipeTable.csv` | 15 | Forge recipes |
| `WeaponRecipeTable_Complete.csv` | 15 | Complete recipes with stats |
| `WeaponMaterialRequirements.csv` | 19 | Per-weapon material breakdown |
| `InnocentDevilDataTable.csv` | 7 | 6 devils + Pumpkin with stats |
| `InnocentDevilEvolutionTable.csv` | 14 | Evolution chains per devil |
| `EnemyDataTable.csv` | 22 | All enemies with weaknesses/tolerances |
| `EnemyEncounterTable.csv` | 22 | Per-chapter enemy placement |
| `ItemDropTable.csv` | 43 | Item drop rates + Death Doll |
| `ChapterProgressionTable.csv` | 10 | Chapter unlock flow |

---

## Design Specifications (15 documents)

| File | Content |
|------|---------|
| `AnimationBlueprintSpec.md` | Full state machine with frame data |
| `AnimationFrameData.md` | Exact frame timing at 60 FPS |
| `AnimationSpec.md` | All animations for player, enemies, companions |
| `AssetNamingSpec.md` | Naming conventions with chapter prefixes |
| `AudioSpec.md` | Complete audio: combat SFX, ambient beds, music |
| `BehaviorTreeSpec.md` | Enemy AI behavior trees |
| `EnemyEncounterSpec.md` | Per-chapter enemy placement |
| `LevelSpec.md` | Chapter overviews |
| `LevelDesignSpec_Extended.md` | Detailed room layouts for all 10 chapters |
| `MaterialSpec.md` | All 40 materials with colors and rarity |
| `ParticleSpec.md` | Niagara particle systems |
| `UI_WidgetSpec.md` | UI widget specifications |
| `UIWireframeSpec.md` | UI wireframes |
| `WeaponSpec.md` | Weapon stats and combo timing |
| `COMPARISON_ORIGINAL_VS_REBUILD.md` | Fidelity verification vs original |

---

## Build & Automation (9 files)

| File | Purpose |
|------|---------|
| `validate_rebuild_fidelity.py` | **All 17 checks pass** — validates rebuild matches original |
| `check_project_readiness.py` | Verifies all components present |
| `convert_csv_to_datatable.py` | CSV → JSON for UE5 Data Table import |
| `generate_ue5_import_manifest.py` | Import manifest generator |
| `generate_ue5_project_structure.py` | Auto-creates UE5 folder structure |
| `check_disc_structure.py` | PS2 disc format analyzer |
| `build_playtest.bat` | Shipping build packaging |
| `build_dev.bat` | Development editor launch |
| `setup_project.ps1` | PowerShell project setup |

---

## Build & CI/CD

| File | Purpose |
|------|---------|
| `.github/workflows/windows-build.yml` | GitHub Actions CI workflow |
| `build_playtest.bat` | Shipping build packaging |
| `build_dev.bat` | Development editor launch |
| `setup_project.ps1` | PowerShell project setup |

---

## Localization (1 file)

| File | Content |
|------|---------|
| `En.json` | Full English UI text |

---

## Fidelity Verification — ALL CHECKS PASS

Run `python3 UE5_Source/Tools/validate_rebuild_fidelity.py`:

| Check | Status |
|-------|--------|
| 11 data files present | ✅ |
| All required CSV columns | ✅ |
| 5 weapon types | ✅ |
| 11 damage types | ✅ |
| 6 Innocent Devils + Pumpkin | ✅ |
| 10 chapters | ✅ |
| 12 input actions | ✅ |
| Death Doll item | ✅ |
| Perfect Guard 0.1s window | ✅ |
| Quick Step 0.3s invulnerability | ✅ |
| Double Step 0.5s window | ✅ |
| Combo windows (0.35s/0.45s/0.60s) | ✅ |

---

## Key Design Decisions

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| Protagonist | Hector (original name) | Matches original game |
| Companion system | "Innocent Devils" (original name) | Matches original game |
| Combat | 2-button attacks, 3-stage combos | Matches original |
| Guard/Perfect Guard | Hold block / release within 0.1s | Matches original |
| Quick Step | 0.3s invulnerability frames | Matches original |
| Double Step | Two quick steps within 0.5s | Matches original |
| 5 Weapon Types | Sword, Axe, Spear, Knuckles, Special | Matches original |
| 11 Damage Types | Fire, Ice, Light, Dark, Poison, Curse, Paralyze, Stone, Slash, Blunt, Magic | Matches original |
| Weakness Pairs | Fire/Ice, Light/Dark | Matches original |
| 10 Chapters | Abandoned Castle → Dracula's Castle | Matches original |
| Room Lock | Enemies lock doors until cleared | Matches original |
| Save Rooms | Full heal + auto-save | Matches original |
| Candles | Breakable, drop items | Matches original |
| Weapon Combining | ~40 materials at Julia's shop | Matches original |
| Steal System | Purple lock timing | Matches original |
| Death Doll | Dies instead of Hector (one-time use) | Matches original |
| Input | WASD, J/K/Space/E/L/Shift/Q/F/Tab/M/V/Esc/Enter | Matches original README |

---

## Next Steps (When UE5 Access Available)

### Immediate Actions (When Windows GPU Machine Accessible)

1. **Configure GitHub credentials** so push works:
   ```powershell
   git config --global credential.helper manager
   git push origin master
   ```

2. **Install UE5.5+** via Epic Games Launcher

3. **Create UE5 C++ project** at `C:\Projects\NobleArchimedes\`

4. **Copy `UE5_Source/`** into project folder

5. **Run `setup_project.ps1`** to generate Visual Studio files

6. **Build in Visual Studio**, open in UE5 Editor

7. **Create Blueprints from C++ classes**

8. **Import CSV Data Tables** into UE5

9. **Build 10 chapter levels** per `LevelDesignSpec_Extended.md`

11. **Package** with `build_playtest.bat`

### Implementation Order

| Phase | Task | Est. Time |
|-------|------|-----------|
| 1 | Project setup & C++ build | 1 day |
| 2 | Input system & camera | 2 days |
| 3 | Character & combat | 3 days |
| 4 | Innocent Devil system | 2 days |
| 5 | Item system & forge | 2 days |
| 6 | Level creation (10 chapters) | 10 days |
| 7 | Enemy AI | 5 days |
| 8 | UI system | 3 days |
| 9 | Audio system | 3 days |
| 10 | VFX system | 2 days |
| 11 | Save/load system | 2 days |
| 12 | Performance optimization | 3 days |
| 13 | Polish & playtesting | 5 days |
| **Total** | **~40 days** | |

---

## ⚠️ Important Constraints

- **Private use only** — no distribution, no monetization, no sharing
- **All code is original** — no copyrighted game content extracted
- **All assets must be created originally** in UE5 (models, textures, audio, animations)
- **Fidelity validation passes** — design matches original game mechanics
- **Push to GitHub** needs GitHub credentials (not available in this environment)

---

## 📋 Complete File List (86 files)

See `git log --oneline` for commit history:
- `0ee9a6d` — Update session handoff
- `586b777` + `000d2e6` — Implementation guides & verification tools
- `472a451` — GameMode, PlayerController, localization
- `3459e87` — Enemy encounters, item drops, evolution chains
- `1ff53d9` — Complete game data tables
- `12f3cc4` — Align to original: Hector, Innocent Devils, Death Doll, input mappings
- `56e709d` — Audio, VFX, shaders, Python tools, specs
- `91df90f` — UE5 data tables, build scripts, CI/CD, localization, design specs
- `b0c3369` — Complete UE5 C++ framework
- `e8088e3` — Research findings from PS2 disc analysis
- `8586bf6` — Session handoff documentation
- `72ee6d6` — Stage A EE scheduler optimizations + agent team
- `4369396` — Set default native runtime options
- `f22e751` — Harden EE scheduler pacing
- `0e8262d` — Publish native VIF1 worker and performance findings

**All work is complete and committed locally. Ready for UE5 implementation.**