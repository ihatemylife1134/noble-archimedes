# UE5 Implementation Checklist

Complete checklist for building Noble Archimedes in Unreal Engine 5.
All code, data tables, and specifications are ready - this checklist tracks the UE5 Editor work.

## Phase 1: Project Setup (Days 1-2)

### 1.1 Project Creation
- [ ] Install Unreal Engine 5.5+
- [ ] Create new C++ Third Person project: `NobleArchimedes`
- [ ] Location: `C:\Projects\NobleArchimedes\`
- [ ] Copy `UE5_Source 5.8/` contents into project folder
- [ ] Run `tools/setup_project.ps1` to generate Visual Studio files
- [ ] Open `NobleArchimedes.sln` in Visual Studio 2022
- [ ] Build Solution (Debug and Shipping configurations)
- [ ] Open `NobleArchimedes.uproject` in UE5 Editor

### 1.2 Project Settings
- [ ] Enable Enhanced Input plugin
- [ ] Enable Lumen plugin
- [ ] Enable Nanite plugin
- [ ] Enable TSR plugin
- [ ] Enable Niagara plugin
- [ ] Enable MediaPlayer plugin
- [ ] Set default map to `Chap_01_AbandonedCastle`
- [ ] Set default game mode to `NobleArchimedesGameModeBase`
- [ ] Set default player class to `BP_HectorCharacter`
- [ ] Set default player controller to `BP_NobleArchimedesPlayerController`

### 1.3 Version Control
- [ ] Initialize Git repository
- [ ] Initialize Git LFS: `git lfs install`
- [ ] Track binary assets: `git lfs track "*.uasset" "*.umap" "*.psd" "*.tga" "*.png" "*.jpg" "*.wav" "*.fbx" "*.obj"`
- [ ] Create `.gitignore` (from `UE5_Source 5.8/.gitignore`)
- [ ] Commit initial project structure

---

## Phase 2: Input System (Days 2-3)

### 2.1 Input Actions
Create in `Content/Input/`:
- [ ] `IA_Move` - Axis2D
- [ ] `IA_Look` - Axis2D
- [ ] `IA_Jump` - Action
- [ ] `IA_AttackLight` - Action
- [ ] `IA_AttackHeavy` - Action
- [ ] `IA_Dodge` - Action
- [ ] `IA_GuardPress` - Action
- [ ] `IA_GuardRelease` - Action
- [ ] `IA_Special` - Action
- [ ] `IA_StealFocus` - Action
- [ ] `IA_LockOn` - Action
- [ ] `IA_Interact` - Action
- [ ] `IA_Menu` - Action
- [ ] `IA_Map` - Action
- [ ] `IA_CameraMode` - Action

### 2.2 Input Mapping Context
- [ ] Create `IMC_Default` in `Content/Input/`
- [ ] Map all keyboard bindings (from `DefaultInput.ini`)
- [ ] Map all gamepad bindings (from `DefaultInput.ini`)
- [ ] Assign to player character

---

## Phase 3: Character & Combat (Days 3-7)

### 3.1 Character Blueprint
- [ ] Create `BP_HectorCharacter` based on `AHectorCharacter` C++ class
- [ ] Add `UCapsuleComponent` (radius 42, height 96)
- [ ] Add `USkeletalMesh` (Hector mesh - create placeholder)
- [ ] Add `UCameraComponent` (follow camera)
- [ ] Add `USpringArmComponent` (camera boom)
- [ ] Add `UNobleArchimedesCombatComponent`
- [ ] Add `UNobleArchimedesCameraComponent`
- [ ] Add `UNobleArchimedesInnocentDevilComponent`
- [ ] Set up input mappings in Blueprint

### 3.2 Weapon Blueprints
Create in `Content/Blueprints/Weapons/`:
- [ ] `BP_Sword_Short`
- [ ] `BP_Sword_Iron`
- [ ] `BP_Sword_Broad`
- [ ] `BP_Sword_Long`
- [ ] `BP_Sword_Great`
- [ ] `BP_Sword_Executioner`
- [ ] `BP_Axe_Battle`
- [ ] `BP_Axe_Great`
- [ ] `BP_Axe_Executioner`
- [ ] `BP_Spear_Long`
- [ ] `BP_Spear_Halberd`
- [ ] `BP_Spear_Pike`
- [ ] `BP_Knuckles_PunchRings`
- [ ] `BP_Knuckles_Claws`
- [ ] `BP_Knuckles_Brass`
- [ ] `BP_Knuckles_Katar`
- [ ] `BP_Special_Shuriken`
- [ ] `BP_Special_Bomb`
- [ ] `BP_Special_Gatling`

### 3.3 Combat Blueprints
- [ ] Create `BP_CombatMontage_Sword`
- [ ] Create `BP_CombatMontage_Axe`
- [ ] Create `BP_CombatMontage_Spear`
- [ ] Create `BP_CombatMontage_Knuckles`
- [ ] Create `BP_CombatMontage_Special`
- [ ] Create `BP_GuardMontage`
- [ ] Create `BP_QuickStepMontage`
- [ ] Create `BP_HitReactionMontage`
- [ ] Create `BP_DeathMontage`

---

## Phase 4: Innocent Devil System (Days 7-9)

### 4.1 Innocent Devil Blueprints
Create in `Content/Blueprints/Companions/`:
- [ ] `BP_Fairy`
- [ ] `BP_Griffin`
- [ ] `BP_Salamander`
- [ ] `BP_Ogre`
- [ ] `BP_SkeletonDevil`
- [ ] `BP_WitchDevil`
- [ ] `BP_Pumpkin`

### 4.2 Innocent Devil AI
- [ ] Implement Auto mode (AI decides actions)
- [ ] Implement Command mode (player direct commands)
- [ ] Implement Guard mode (block and distract)
- [ ] Implement evolution system (Evo Crystal)
- [ ] Implement level progression

---

## Phase 5: Item System (Days 9-10)

### 5.1 Item Blueprints
Create in `Content/Blueprints/Items/`:
- [ ] `BP_Potion` (heals 50 HP)
- [ ] `BP_HighPotion` (heals 150 HP)
- [ ] `BP_Serum` (cures poison/curse)
- [ ] `BP_Uncurse` (removes curse)
- [ ] `BP_DeathDoll` (dies instead of Hector)
- [ ] `BP_Material_Base` (base material class)

### 5.2 Material Blueprints (~40 materials)
Create in `Content/Blueprints/Items/Materials/`:
- [ ] `BP_Material_IronShard`
- [ ] `BP_Material_SilverIngot`
- [ ] `BP_Material_DarkCrystal`
- [ ] `BP_Material_HolyWater`
- [ ] `BP_Material_PhoenixFeather`
- [ ] `BP_Material_DragonScale`
- [ ] `BP_Material_DemonBone`
- [ ] `BP_Material_GhostEssence`
- [ ] `BP_Material_WizardsOrb`
- [ ] `BP_Material_MithrilOre`
- [ ] `BP_Material_Adamantite`
- [ ] `BP_Material_Orichalcum`
- [ ] `BP_Material_PhoenixDown`
- [ ] `BP_Material_UnicornHorn`
- [ ] `BP_Material_DragonHeart`
- [ ] `BP_Material_DemonSoul`
- [ ] `BP_Material_AngelFeather`
- [ ] `BP_Material_VampireFang`
- [ ] `BP_Material_WerewolfClaw`
- [ ] `BP_Material_GolemCore`
- [ ] `BP_Material_FairyDust`
- [ ] `BP_Material_WitchBroom`
- [ ] `BP_Material_ZombieBrain`
- [ ] `BP_Material_GhoulEye`
- [ ] `BP_Material_HarpyFeather`
- [ ] `BP_Material_BasiliskScale`
- [ ] `BP_Material_MedusaHair`
- [ ] `BP_Material_CerberusFang`
- [ ] `BP_Material_HydraBlood`
- [ ] `BP_Material_ChimeraHorn`
- [ ] `BP_Material_GriffinFeather`
- [ ] `BP_Material_SphinxEye`
- [ ] `BP_Material_MinotaurHorn`
- [ ] `BP_Material_CyclopsEye`
- [ ] `BP_Material_TrollSkin`
- [ ] `BP_Material_OgreClub`
- [ ] `BP_Material_GiantToe`
- [ ] `BP_Material_LeviathanScale`
- [ ] `BP_Material_KrakenTentacle`
- [ ] `BP_Material_SeaSerpentFang`

---

## Phase 6: Weapon Forge System (Days 10-11)

### 6.1 Forge UI
- [ ] Create `WB_WeaponForge` widget
- [ ] Material inventory display
- [ ] Recipe list display
- [ ] Result preview
- [ ] Forge/Cancel buttons

### 6.2 Forge Logic
- [ ] Implement material combination logic
- [ ] Implement recipe validation
- [ ] Implement material consumption
- [ ] Implement weapon spawning

---

## Phase 7: Level Design (Days 11-20)

### 7.1 Chapter Levels
Create in `Content/Maps/`:
- [ ] `PersistentLevel.umap`
- [ ] `Chap_01_AbandonedCastle.umap`
- [ ] `Chap_02_BaljhetMountains.umap`
- [ ] `Chap_03_GaribaldiTemple.umap`
- [ ] `Chap_04_MortviaAqueduct.umap`
- [ ] `Chap_05_ForestOfJigramunt.umap`
- [ ] `Chap_06_CordovaTown.umap`
- [ ] `Chap_07_EneomaosMachineTower.umap`
- [ ] `Chap_08_AiolonRuins.umap`
- [ ] `Chap_09_InfiniteCorridor.umap`
- [ ] `Chap_10_DraculasCastle.umap`

### 7.2 Level Streaming
- [ ] Set up Level Streaming Volumes
- [ ] Configure chapter transitions
- [ ] Set up PersistentLevel (player, UI, save system)
- [ ] Test chapter-to-chapter transitions

### 7.3 Room Systems
- [ ] Implement room lock mechanics
- [ ] Implement save rooms (full heal + auto-save)
- [ ] Implement candles (breakable, drop items)
- [ ] Implement green door rooms (Innocent Devil acquisition)
- [ ] Implement Map Checker (colored X markers)

---

## Phase 8: Enemy System (Days 20-25)

### 8.1 Enemy Blueprints
Create in `Content/Blueprints/Enemies/`:
- [ ] `BP_Enemy_Skeleton`
- [ ] `BP_Enemy_Zombie`
- [ ] `BP_Enemy_Ghoul`
- [ ] `BP_Enemy_Harpy`
- [ ] `BP_Enemy_Bat`
- [ ] `BP_Enemy_MountainBeast`
- [ ] `BP_Enemy_TempleGuardian`
- [ ] `BP_Enemy_Cultist`
- [ ] `BP_Enemy_DarkPriest`
- [ ] `BP_Enemy_WaterCreature`
- [ ] `BP_Enemy_AqueductGuard`
- [ ] `BP_Enemy_ForestStalker`
- [ ] `BP_Enemy_NatureSpirit`
- [ ] `BP_Enemy_TownGuard`
- [ ] `BP_Enemy_Citizen`
- [ ] `BP_Enemy_ClockworkSoldier`
- [ ] `BP_Enemy_MechanicalTrap`
- [ ] `BP_Enemy_RuinGuardian`
- [ ] `BP_Enemy_AncientConstruct`
- [ ] `BP_Enemy_CorridorPhantom`
- [ ] `BP_Enemy_SurrealEntity`
- [ ] `BP_Enemy_CastleElite`
- [ ] `BP_Enemy_FinalBoss`

### 8.2 Boss Blueprints
Create in `Content/Blueprints/Enemies/Bosses/`:
- [ ] `BP_Boss_SentinelKnight` (Chapter 1)
- [ ] `BP_Boss_SkyDrake` (Chapter 2)
- [ ] `BP_Boss_HighInquisitor` (Chapter 3)
- [ ] `BP_Boss_AqueductSentinel` (Chapter 4)
- [ ] `BP_Boss_ForestWarden` (Chapter 5)
- [ ] `BP_Boss_TownCaptain` (Chapter 6)
- [ ] `BP_Boss_TowerAutomaton` (Chapter 7)
- [ ] `BP_Boss_RuinSentinel` (Chapter 8)
- [ ] `BP_Boss_MirrorEntity` (Chapter 9)
- [ ] `BP_Boss_FinalBoss` (Chapter 10)

### 8.3 AI Behavior Trees
- [ ] Create behavior tree for each enemy type
- [ ] Implement patrol, chase, attack states
- [ ] Implement steal vulnerability states
- [ ] Implement boss phase transitions

---

## Phase 8: UI System (Days 25-28)

### 8.1 UI Widgets
Create in `Content/UI/`:
- [ ] `WB_MainMenu`
- [ ] `WB_HUD` (health, mana, combo, weapon, companion)
- [ ] `WB_PauseMenu`
- [ ] `WB_SaveLoad`
- [ ] `WB_WeaponForge`
- [ ] `WB_InnocentDevilStatus`
- [ ] `WB_ComboCounter`
- [ ] `WB_Map`

### 8.2 UI Logic
- [ ] Health/Mana binding to character stats
- [ ] Combo counter binding to combat component
- [ ] Weapon icon binding to equipped weapon
- [ ] Innocent Devil icon binding to active companion
- [ ] Save/load slot display
- [ ] Forge UI integration

---

## Phase 9: Audio System (Days 28-30)

### 9.1 Sound Cues
Create in `Content/Audio/SFX/`:
- [ ] `SC_Combat_Swing_Sword`
- [ ] `SC_Combat_Swing_Axe`
- [ ] `SC_Combat_Swing_Spear`
- [ ] `SC_Combat_Swing_Knuckles`
- [ ] `SC_Combat_Swing_Special`
- [ ] `SC_Combat_WeaponHit`
- [ ] `SC_Combat_PlayerHit`
- [ ] `S_Combat_EnemyHit`
- [ ] `SC_Combat_QuickStep`
- [ ] `SC_Combat_GuardBlock`
- [ ] `SC_Combat_PerfectGuard`
- [ ] `SC_Combat_Death`
- [ ] `SC_Combat_BossTheme`
- [ ] `SC_InnocentDevilSummon`
- [ ] `SC_InnocentDevilAttack`
- [ ] `SC_InnocentDevilEvolve`
- [ ] `SC_Item_Pickup`
- [ ] `SC_Item_Potion`
- [ ] `SC_Item_HighPotion`
- [ ] `SC_Item_Serum`
- [ ] `SC_Item_Uncurse`
- [ ] `SC_Item_Steal`
- [ ] `S_UI_Click`
- [ ] `S_UI_MenuOpen`
- [ ] `S_UI_Save`

### 9.2 Ambient Audio
Create in `Content/Audio/Ambient/`:
- [ ] `SC_Amb_Castle`
- [ ] `SC_Amb_Mountains`
- [ ] `SC_Amb_Temple`
- [ ] `SC_Amb_Aqueduct`
- [ ] `SC_Amb_Forest`
- [ ] `SC_Amb_Town`
- [ ] `SC_Amb_Tower`
- [ ] `SC_Amb_Ruins`
- [ ] `SC_Amb_Corridor`
- [ ] `SC_Amb_CastleFinal`

### 9.3 Music
Create in `Content/Audio/Music/`:
- [ ] `SC_Music_Chap01` through `SC_Music_Chap10`
- [ ] `SC_Music_Combat`
- [ ] `SC_Music_Boss`
- [ ] `S_Music_Victory`
- [ ] `S_Music_GameOver`

---

## Phase 10: VFX System (Days 30-32)

### 10.1 Niagara Systems
Create in `Content/VFX/`:
- [ ] `NS_WeaponTrail_Sword`
- [ ] `NS_WeaponTrail_Axe`
- [ ] `NS_WeaponTrail_Spear`
- [ ] `NS_WeaponTrail_Knuckles`
- [ ] `NS_WeaponTrail_Special`
- [ ] `NS_HitSpark_Fire`
- [ ] `NS_HitSpark_Ice`
- [ ] `NS_HitSpark_Light`
- [ ] `NS_HitSpark_Dark`
- [ ] `NS_HitBlood`
- [ ] `NS_QuickStepTrail`
- [ ] `NS_PerfectGuardFlash`
- [ ] `NS_GuardBlockFlash`
- [ ] `NS_InnocentDevilSummon`
- [ ] `NS_InnocentDevilEvolve`
- [ ] `NS_InnocentDevilAttack`
- [ ] `NS_ItemPickup`
- [ ] `NS_CandleBreak`
- [ ] `NS_SaveRoomHeal`
- [ ] `NS_DustMotes_Castle`
- [ ] `NS_Leaves_Forest`
- [ ] `NS_Steam_MachineTower`

---

## Phase 11: Save/Load System (Days 32-33)

### 11.1 Save Game Integration
- [ ] Connect SaveGame class to UI
- [ ] Implement save slot UI
- [ ] Implement auto-save triggers
- [ ] Implement load game flow
- [ ] Implement delete save functionality

### 11.2 Testing
- [ ] Test save/load across chapters
- [ ] Test save room auto-save
- [ ] Test manual save from pause menu
- [ ] Test save file corruption recovery

---

## Phase 12: Performance Optimization (Days 33-35)

### 12.1 Profiling
- [ ] Profile frame time in each chapter
- [ ] Profile memory usage per chapter
- [ ] Profile level streaming hitches
- [ ] Profile audio CPU usage

### 12.2 Optimization
- [ ] Set LODs for character models
- [ ] Set texture compression settings
- [ ] Set audio compression settings
- [ ] Configure level streaming volumes
- [ ] Enable occlusion culling
- [ ] Bake Lightmass lighting

---

## Phase 13: Final Polish (Days 35-40)

### 13.1 Polish
- [ ] Fix all bugs found during playtesting
- [ ] Balance combat difficulty
- [ ] Balance enemy encounters
- [ ] Polish visual effects
- [ ] Polish audio mixing
- [ ] Polish UI transitions

### 13.2 Final Build
- [ ] Package Shipping build
- [ ] Test packaged build
- [ ] Create release notes
- [ ] Create installation instructions

---

## Total Estimated Time: 40 Days

**Note:** All C++ code, data tables, and specifications are complete. The remaining work is UE5 Editor work: creating Blueprints, importing assets, building levels, and packaging.
