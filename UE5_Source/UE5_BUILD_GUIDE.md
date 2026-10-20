# Noble Archimedes — UE5 Build Guide (Step-by-Step)

## Prerequisites
- UE5.8 installed at `C:\Program Files\Epic Games\UE_5.8`
- Project directory: `C:\Projects\NobleArchimedes`
- All source files copied from `UE5_Source/` to `C:\Projects\NobleArchimedes\`
- C++ code compiles successfully ✅

---

## Step 1: Create Blueprints from C++ Classes

### 1.1 Open the project in UE5 Editor
1. Launch UE5 Editor
2. File > Open Project > `C:\Projects\NobleArchimedes\NobleArchimedes.uproject`
3. Wait for C++ module to compile (should succeed)

### 1.2 Create Blueprint classes
In the Content Browser, navigate to `Content/Blueprints/` (create if needed).

For each C++ class below, right-click > **Create Blueprint Class based on**:

| C++ Class | Blueprint Name | Location |
|-----------|---------------|----------|
| `AHectorCharacter` | `BP_HectorCharacter` | Content/Blueprints/Characters/ |
| `ARoom` | `BP_Room` | Content/Blueprints/Levels/ |
| `ASaveRoom` | `BP_SaveRoom` | Content/Blueprints/Levels/ |
| `ACandleBreakable` | `BP_CandleBreakable` | Content/Blueprints/Levels/ |
| `AEnemyBase` | `BP_EnemyBase` | Content/Blueprints/Enemies/ |
| `ABossBase` | `BP_BossBase` | Content/Blueprints/Enemies/ |
| `AInnocentDevilActor` | `BP_InnocentDevilActor` | Content/Blueprints/InnocentDevils/ |
| `AItemDrop` | `BP_ItemDrop` | Content/Blueprints/Items/ |
| `AMapChecker` | `BP_MapChecker` | Content/Blueprints/Levels/ |
| `ANobleArchimedesHUD` | `BP_NobleArchimedesHUD` | Content/Blueprints/UI/ |
| `UNobleArchimedesGameModeBase` | `BP_NobleArchimedesGameModeBase` | Content/Blueprints/Core/ |

### 1.3 Configure GameMode
1. Open `BP_NobleArchimedesGameModeBase`
2. Set **Default Pawn Class** = `BP_HectorCharacter`
3. Set **HUD Class** = `BP_NobleArchimedesHUD`
4. Save

### 1.4 Set up GameInstance
1. Edit > Project Settings > Maps & Modes
2. Set **Game Instance Class** = `UNobleArchimedesGameInstance`

---

## Step 2: Import CSV Data Tables

### 2.1 Import each CSV as a Data Table
In Content Browser: Right-click > **Miscellaneous > Data Table**

| CSV File | Row Structure | Output Asset Name |
|----------|--------------|-------------------|
| `WeaponDataTable.csv` | `FWeaponData` | `DT_WeaponData` |
| `MaterialDataTable.csv` | `FMaterialData` | `DT_MaterialData` |
| `WeaponRecipeTable_Complete.csv` | `FWeaponRecipe` | `DT_WeaponRecipe` |
| `InnocentDevilDataTable.csv` | `FInnocentDevilData` | `DT_InnocentDevilData` |
| `EnemyDataTable.csv` | `FEnemyData` | `DT_EnemyData` |
| `EnemyEncounterTable.csv` | `FEnemyEncounter` | `DT_EnemyEncounter` |
| `ItemDropTable.csv` | `FItemDropData` | `DT_ItemDrop` |
| `InnocentDevilEvolutionTable.csv` | `FInnocentDevilEvolution` | `DT_InnocentDevilEvolution` |
| `WeaponMaterialRequirements.csv` | `FWeaponMaterialRequirement` | `DT_WeaponMaterialReq` |
| `ChapterProgressionTable.csv` | `FChapterProgression` | `DT_ChapterProgression` |
| `WeaponRecipeTable.csv` | `FWeaponRecipe` | `DT_WeaponRecipeBasic` |

### 2.2 Wire Data Tables to C++ Components
For each component that uses data tables, assign the imported Data Table asset in the Blueprint's Defaults panel:
- `BP_HectorCharacter` → CombatComponent → WeaponDataTable = `DT_WeaponData`
- `BP_WeaponForge` (if created) → WeaponRecipes = `DT_WeaponRecipe`, MaterialData = `DT_MaterialData`

---

## Step 3: Build 10 Chapter Levels

Create a new level for each chapter. Place actors per `LevelSpec.md` and `LevelDesignSpec_Extended.md`.

### Chapter 1: Abandoned Castle
- **Rooms**: Entrance Hall (3 Skeletons, 2 Zombies), Chapel (2 Ghouls), Save Room, Boss Arena (Sentinel Knight)
- **Actors**: BP_Room (per room), BP_SaveRoom (save room), BP_CandleBreakable (chapel candles)
- **Special**: Green door room with Fairy acquisition
- **Key Items**: Short Sword recipe, Potion x3

### Chapter 2: Baljhet Mountains
- **Rooms**: Mountain Pass (4 Harpies), Cave Entrance (6 Bats), Summit (2 Mountain Beasts), Boss Arena (Sky Drake)
- **Actors**: BP_Room, BP_CandleBreakable
- **Special**: Griffin acquisition

### Chapter 3: Garibaldi Temple
- **Rooms**: Nave (3 Temple Guardians), Crypt (4 Cultists), Bell Tower (2 Dark Priests), Boss Arena (High Inquisitor)
- **Actors**: BP_Room, BP_SaveRoom (if any), BP_CandleBreakable
- **Special**: Salamander acquisition

### Chapter 4: Mortvia Aqueduct
- **Rooms**: Upper Aqueduct (3 Water Creatures), Water Chamber (2 Aqueduct Guards), Bridge Crossing (no enemies), Boss Arena (Aqueduct Sentinel)
- **Actors**: BP_Room, BP_CandleBreakable
- **Special**: Ogre acquisition

### Chapter 5: Forest of Jigramunt
- **Rooms**: Forest Edge (4 Forest Stalkers), Deep Forest (3 Nature Spirits), Grove (no enemies), Boss Arena (Forest Warden)
- **Actors**: BP_Room, BP_CandleBreakable
- **Special**: Skeleton Devil acquisition

### Chapter 6: Cordova Town
- **Rooms**: Town Square (5 Town Guards), Market (safe), Julia's Shop (forge), Save Room, Boss Arena (Town Captain)
- **Actors**: BP_Room, BP_SaveRoom, BP_CandleBreakable
- **Special**: Witch Devil acquisition, Weapon Forge at Julia's Shop

### Chapter 7: Eneomaos Machine Tower
- **Rooms**: Gear Chamber (4 Clockwork Soldiers), Elevator Shaft (no enemies), Steam Room (6 Mechanical Traps), Boss Arena (Tower Automaton)
- **Actors**: BP_Room, BP_CandleBreakable
- **Special**: Pumpkin acquisition (secret)

### Chapter 8: Aiolon Ruins
- **Rooms**: Ruin Entrance (3 Ruin Guardians), Glyph Chamber (no enemies), Sunken Courtyard (2 Ancient Constructs), Boss Arena (Ruin Sentinel)
- **Actors**: BP_Room, BP_CandleBreakable
- **Special**: Map Checker upgrade

### Chapter 9: Infinite Corridor
- **Rooms**: Corridor Loop (5 Corridor Phantoms), Mirror Chamber (3 Surreal Entities), Void Space (no enemies), Boss Arena (Mirror Entity)
- **Actors**: BP_Room, BP_CandleBreakable

### Chapter 10: Dracula's Castle
- **Rooms**: Grand Hall (6 Castle Elite), Throne Room (no enemies), Boss Rush Area (all previous bosses), Boss Arena (Final Boss)
- **Actors**: BP_Room, BP_CandleBreakable

### Level Setup Checklist (per chapter)
- [ ] Create level file (`Chap_XX_Name`)
- [ ] Place BP_Room actors for each room
- [ ] Configure enemy spawn classes and locations
- [ ] Place BP_SaveRoom in save room locations
- [ ] Place BP_CandleBreakable at candle positions
- [ ] Place BP_MapChecker (if applicable)
- [ ] Set room exit connections
- [ ] Configure lighting per LevelSpec
- [ ] Set spawn point for player

---

## Step 4: Create UMG Widgets

Create Widget Blueprints (`.uasset`) for each UI screen per `UI_WidgetSpec.md` and `UIWireframeSpec.md`:

| Widget | Location | Purpose |
|--------|----------|---------|
| `WB_MainMenu` | Content/UI/ | New Game, Load Game, Options, Quit |
| `WB_HUD` | Content/UI/ | Health, Mana, Combo, Weapon, ID status, Chapter |
| `WB_PauseMenu` | Content/UI/ | Resume, Save, Load, Options, Quit |
| `WB_SaveLoad` | Content/UI/ | 6 save slots with info |
| `WB_WeaponForge` | Content/UI/ | Material inventory, recipe list, preview |
| `WB_InnocentDevilStatus` | Content/UI/ | ID portrait, level, HP, mode, abilities |
| `WB_ComboCounter` | Content/UI/ | Combo count with timing ring |

### Widget Setup
1. Create each widget as `UserWidget` Blueprint
2. Add UI elements per wireframe specs
3. Bind health/mana to HectorCharacter stats
4. Bind combo counter to CombatComponent
5. Bind weapon icon to equipped weapon
6. Bind Innocent Devil icon to active companion

---

## Step 5: Create Sound Cues

Per `AudioSpec.md`, create 74 Sound Cue assets (`SC_*`) in `Content/Audio/`:

### Combat (16)
- `SC_Combat_Swing_Sword/Axe/Spear/Knuckles/Special` (5)
- `SC_Combat_Hit_Sword/Axe/Spear/Knuckles/Special` (5)
- `SC_Combat_PlayerHit`, `SC_Combat_EnemyHit`, `SC_Combat_QuickStep`, `SC_Combat_GuardBlock`, `SC_Combat_PerfectGuard`, `SC_Combat_Death`

### Innocent Devil (10)
- `SC_InnocentDevil_Summon_Fairy/Griffin/Salamander/Ogre/Skeleton/Witch/Pumpkin` (7)
- `SC_InnocentDevil_Attack`, `SC_InnocentDevil_Evolve`, `SC_InnocentDevil_Hit`

### Item (8)
- `SC_Item_Pickup`, `SC_Item_Potion`, `SC_Item_HighPotion`, `SC_Item_Serum`, `SC_Item_Uncurse`, `SC_Item_Steal`, `SC_Item_StealFail`, `SC_Item_Forge`

### Environment (9)
- `SC_Env_CandleBreak`, `SC_Env_DoorOpen`, `SC_Env_DoorClose`, `SC_Env_ChestOpen`, `SC_Env_SaveRoom`
- `SC_Env_Footstep_Stone`, `SC_Env_Footstep_Wood`, `SC_Env_Footstep_Metal`, `SC_Env_Footstep_Dirt`

### UI (7)
- `SC_UI_Click`, `SC_UI_Hover`, `SC_UI_MenuOpen`, `SC_UI_MenuClose`, `SC_UI_Save`, `SC_UI_Load`, `SC_UI_Error`

### Ambient (10)
- `SC_Amb_Castle`, `SC_Amb_Mountains`, `SC_Amb_Temple`, `SC_Amb_Aqueduct`, `SC_Amb_Forest`, `SC_Amb_Town`, `SC_Amb_Tower`, `SC_Amb_Ruins`, `SC_Amb_Corridor`, `SC_Amb_CastleFinal`

### Music (14)
- `SC_Music_Chap01` through `SC_Music_Chap10` (10)
- `SC_Music_Combat`, `SC_Music_Boss`, `SC_Music_Victory`, `SC_Music_GameOver`

### Assign Sound Cues
In each Blueprint (e.g., `BP_AudioComponent`), assign the Sound Cue assets to the `USoundCue*` member variables.

---

## Step 6: Create Niagara Systems

Per `ParticleSpec.md`, create 31 Niagara Systems (`NS_*`) in `Content/VFX/`:

### Combat (13)
- `NS_WeaponTrail_Sword/Axe/Spear/Knuckles/Special` (5)
- `NS_HitSpark_Fire/Ice/Light/Dark` (4)
- `NS_HitBlood`, `NS_QuickStepTrail`, `NS_PerfectGuardFlash`, `NS_GuardBlockFlash`

### Innocent Devil (12)
- `NS_InnocentDevilSummon_Fairy/Griffin/Salamander/Ogre/Skeleton/Witch/Pumpkin` (7)
- `NS_InnocentDevilEvolve`, `NS_InnocentDevilAttack_Fire/Ice/Light/Dark` (4)

### Item (3)
- `NS_ItemPickup`, `NS_CandleBreak`, `NS_SaveRoomHeal`

### Ambient (3)
- `NS_DustMotes_Castle`, `NS_Leaves_Forest`, `NS_Steam_MachineTower`

### Assign Niagara Systems
In each Blueprint (e.g., `BP_VFXComponent`), assign the Niagara System assets to the `UNiagaraSystem*` member variables.

---

## Step 7: Create Animation Blueprints

Per `AnimationBlueprintSpec.md` and `AnimationFrameData.md`:

### 7.1 Create AnimBP
1. Create `ABP_Hector` Animation Blueprint based on `BP_HectorCharacter`'s skeleton
2. Set up Idle/Walk/Run blend space (`BS_Locomotion`)
3. Create Attack montages for each weapon type (`AM_Combo_Sword`, etc.)
4. Create Guard, Quick Step, Hit Reaction, Death montages
5. Set up state machine transitions per spec:
   - Idle → Walk/Run (speed-based)
   - Idle → Light Attack 1 → Light Attack 2 → Light Attack 3 → Heavy Attack
   - Any Attack → Idle (combo window expired)
   - Idle → Guard Start → Guard Loop → Guard Release → Perfect Guard / Idle
   - Idle → Quick Step → Idle
   - Any State → Hit Reaction → Idle
   - Any State → Death

### 7.2 Animation Notifies
Add notifies per `AnimationBlueprintSpec.md`:
- `NS_WeaponSwingStart` (frame 2)
- `NS_WeaponSwingHit` (frames 4-6)
- `NS_WeaponSwingEnd` (frame 8)
- `NS_QuickStepStart` (frame 1)
- `NS_QuickStepEnd` (frame 18)
- `NS_GuardStart`, `NS_GuardEnd`, `NS_PerfectGuard`
- `NS_Footstep_L`, `NS_Footstep_R`
- `NS_ItemPickup`, `NS_ItemUse`

### 7.3 Timing Windows
- Combo Stage 1: 21 frames (0.35s)
- Combo Stage 2: 27 frames (0.45s)
- Combo Stage 3: 36 frames (0.60s)
- Perfect Guard: 6 frames (0.1s)
- Quick Step iframes: 18 frames (0.3s)

---

## Step 8: Create Behavior Trees

Per `BehaviorTreeSpec.md`:

### 8.1 Create Blackboard
Create `BB_EnemyBase` with all 11 blackboard keys:
- Player (Object), CanSeePlayer (Bool), IsInAttackRange (Bool), IsNotInAttackRange (Bool)
- PatrolPoint (Vector), PatrolIndex (Int), AttackTimer (Float), AttackCooldown (Float)
- StealWindow (Float), IsStealable (Bool), DetectRadius (Float), AttackRadius (Float)

### 8.2 Create Behavior Trees
For each enemy type, create `BT_EnemyName` with:
- Selector: Root
  - Sequence: Combat (CanSeePlayer + IsInAttackRange → FacePlayer → PlayAttackAnimation)
  - Sequence: Chase (CanSeePlayer + IsNotInAttackRange → MoveToPlayer → PlayChaseAnimation)
  - Sequence: Patrol (CannotSeePlayer → MoveToPatrolPoint → WaitAtPatrolPoint)
  - Sequence: Idle (CannotSeePlayer + AtPatrolPoint → PlayIdleAnimation)

### 8.3 Create Services
- `UpdateCanSeePlayer` (0.1s tick)
- `UpdateIsInAttackRange` (0.1s tick)
- `UpdateStealWindow` (0.1s tick)
- `UpdatePatrolPoint` (1.0s tick)

### 8.4 Create Tasks
- FacePlayer, MoveToPlayer, MoveToPatrolPoint, WaitAtPatrolPoint, PlayAttackAnimation, PlayChaseAnimation, PlayIdleAnimation, CheckStealWindow, ApplyDamage

### 8.5 Create Decorators
- CanSeePlayer, IsInAttackRange, IsNotInAttackRange, CanSteal, IsOnPatrol

### 8.6 Boss AI
For each boss, create multi-phase behavior tree per `BehaviorTreeSpec.md` Section 8 (2-3 phases per boss).

---

## Step 9: Set Up Input Mapping Context

Create `IMC_Default` Input Mapping Context in `Content/Input/`:

| Action | Keyboard | Gamepad (XInput) |
|--------|----------|------------------|
| Move | WASD | Left Stick |
| Look | Mouse | Right Stick |
| Jump | Space | A / Cross |
| Light Attack | J | X / Square |
| Heavy Attack | K | Y / Triangle |
| Dodge | Shift + Dir | B / Circle + Dir |
| Guard (Hold) | Left Shift | L1 / LB |
| Guard Release | Left Shift (release) | L1 / LB (release) |
| Special | Q | LT / L2 |
| Interact | E / L | A / Cross |
| Menu | Esc / Enter | Start / Options |
| Map | M | Select / Touchpad |
| Camera Mode | V | R3 / Rstick click |

Assign `IMC_Default` to the Enhanced Input Local Player Subsystem in `BP_HectorCharacter` or `BP_PlayerController`.

---

## Step 10: Configure Project Settings

1. **Edit > Project Settings > Maps & Modes**
   - GameMode Override: `BP_NobleArchimedesGameModeBase`
   - Game Instance Class: `UNobleArchimedesGameInstance`
   - Default Maps: Set Editor Startup Map and Game Default Map to `Chap_01_AbandonedCastle`

2. **Edit > Project Settings > Input**
   - Verify `IMC_Default` is registered in `DefaultInput.ini`

3. **Edit > Project Settings > Packaging**
   - Set build configuration to Shipping
   - Enable blueprint nativization if needed

4. **DefaultEngine.ini** — ensure settings are appropriate:
   - `+ServerTravelTransitionMap=/Game/Maps/Transition` — create this map or remove reference

---

## Step 11: Package with build_playtest.bat

1. Run `C:\Projects\NobleArchimedes\BuildScripts\build_playtest.bat`
2. Wait for BuildCookRun to complete (10-30 minutes)
3. Output: `C:\Projects\NobleArchimedes\Saved\StagedBuilds\Windows\NobleArchimedes\NobleArchimedes.exe`
4. Test the build by launching the executable

---

## Quick Reference: File Locations

| Asset Type | Source | UE5 Location |
|------------|--------|--------------|
| C++ Headers | `UE5_Source/NobleArchimedes/Public/` | `Source/NobleArchimedes/Public/` |
| C++ Source | `UE5_Source/NobleArchimedes/Private/` | `Source/NobleArchimedes/Private/` |
| Data Tables | `UE5_Source/Content/DataTables/*.csv` | `Content/DataTables/` (import as Data Table) |
| Design Specs | `UE5_Source/Content/Blueprints/*.md` | Reference only |
| Level Specs | `UE5_Source/Content/Blueprints/LevelSpec.md` | Reference only |
| Audio Spec | `UE5_Source/Content/Blueprints/AudioSpec.md` | Reference for Sound Cue creation |
| VFX Spec | `UE5_Source/Content/Blueprints/ParticleSpec.md` | Reference for Niagara creation |
| Animation Spec | `UE5_Source/Content/Blueprints/AnimationBlueprintSpec.md` | Reference for AnimBP creation |
| AI Spec | `UE5_Source/Content/Blueprints/BehaviorTreeSpec.md` | Reference for BT creation |
| UI Spec | `UE5_Source/Content/Blueprints/UI_WidgetSpec.md` | Reference for UMG creation |
| Level Design | `UE5_Source/Content/Blueprints/LevelDesignSpec_Extended.md` | Reference for level layout |

---

## Validation Tools

Run before each build:
- `python UE5_Source/Tools/validate_rebuild_fidelity.py` — fidelity checks
- `python UE5_Source/Tools/check_project_readiness.py` — component readiness
- `python UE5_Source/Tools/validate_data_tables.py` — data table validation

---

**All code compiles successfully for UE5.8. The remaining work is editor-side content creation (Blueprints, levels, assets, animations, audio, VFX).**
