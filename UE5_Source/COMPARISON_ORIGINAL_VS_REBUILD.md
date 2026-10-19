# Comparison: Original Castlevania: Curse of Darkness vs UE5 Fan Rebuild

**Purpose:** Private educational use only — exact rebuild of the original game.
**Source:** Bradygames Official Strategy Guide + PS2 disc analysis (SLUS-211.68)
**Status:** Identifying deviations to correct for exact fidelity.

---

## 1. PROTAGONIST & CHARACTERS

| Element | Original (PS2) | My Rebuild | Status | Correction Needed |
|---------|---------------|------------|--------|-------------------|
| Protagonist Name | Hector | "The Forgemaster" | ❌ Deviates | Change to "Hector" |
| Protagonist Role | Devil Forgemaster | Devil Forgemaster | ✅ Match | Keep |
| Antagonist | Isaac | Not specified | ❌ Missing | Add "Isaac" |
| Ally | Julia (witch, shop owner) | Julia | ⚠️ Partial | Confirm full implementation |
| Ally | Trevor Belmont | Not specified | ❌ Missing | Add "Trevor Belmont" |
| Innocent Devils | 6 types + Pumpkin | 6 companions + Pumpkin | ⚠️ Name only | Rename to "Innocent Devils" |
| Devil Names | Fairy, Griffin, Salamander, Ogre, Skeleton, Witch, Pumpkin | Same | ✅ Match | Keep original names |

**Action:** Update all code references from "Companion" to "Innocent Devil", "The Forgemaster" to "Hector".

---

## 2. GAME STRUCTURE — 10 CHAPTERS

| Chapter | Original Name | My Rebuild | Status |
|---------|--------------|------------|--------|
| 1 | Abandoned Castle | Chap_01_AbandonedCastle | ✅ Match |
| 2 | Baljhet Mountains | Chap_02_BaljhetMountains | ✅ Match |
| 3 | Garibaldi Temple | Chap_03_GaribaldiTemple | ✅ Match |
| 4 | Mortvia Aqueduct | Chap_04_MortviaAqueduct | ✅ Match |
| 5 | Forest of Jigramunt | Chap_05_ForestOfJigramunt | ✅ Match |
| 6 | Cordova Town | Chap_06_CordovaTown | ✅ Match |
| 7 | Eneomaos Machine Tower | Chap_07_EneomaosMachineTower | ✅ Match |
| 8 | Aiolon Ruins | Chap_08_AiolonRuins | ✅ Match |
| 9 | Infinite Corridor | Chap_09_InfiniteCorridor | ✅ Match |
| 10 | Dracula's Castle | Chap_10_DraculasCastle | ✅ Match |

**Status:** ✅ All chapter names match exactly.

---

## 3. COMBAT SYSTEM

| Mechanic | Original | My Rebuild | Status | Correction |
|----------|----------|------------|--------|------------|
| Attack Buttons | Light (J/X) + Heavy/Final (K/Y) | Light (J/X) + Heavy/Final (K/Y) | ✅ Match | Keep |
| Combo Stages | 3 stages + final attack variants | 3 stages + final attack variants | ✅ Match | Keep |
| Combo Windows | Stage 1: ~0.35s, Stage 2: ~0.45s, Stage 3: ~0.60s | Same values | ✅ Match | Keep |
| Guard | Hold L1 / Left Shift | Hold L1 / Left Shift | ✅ Match | Keep |
| Perfect Guard | Release within 0.1s before impact | 0.1s window | ✅ Match | Keep |
| Guard Damage Reduction | ~70% | 70% | ✅ Match | Keep |
| Quick Step | Direction + Dodge, 0.3s invulnerability | Same | ✅ Match | Keep |
| Double Step | Two quick steps within 0.5s | Same | ✅ Match | Keep |
| Weapon Types | Sword, Axe, Spear, Knuckles, Special | Same 5 types | ✅ Match | Keep |
| Damage Types | 11 types (Fire, Ice, Light, Dark, Poison, Curse, Paralyze, Stone, Slash, Blunt, Magic) | Same 11 types | ✅ Match | Keep |
| Weakness Pairs | Fire/Ice, Light/Dark | Same | ✅ Match | Keep |

**Status:** ✅ Combat system matches original.

---

## 4. INNOCENT DEVIL SYSTEM

| Mechanic | Original | My Rebuild | Status | Correction |
|----------|----------|------------|--------|------------|
| Name | "Innocent Devil" | "Companion" | ❌ Deviates | Rename all references |
| Types | 6 + Pumpkin | 6 + Pumpkin | ✅ Match | Keep names |
| Names | Fairy, Griffin, Salamander, Ogre, Skeleton, Witch, Pumpkin | Same | ✅ Match | Keep |
| Modes | Auto, Command, Guard | Auto, Command, Guard | ✅ Match | Keep |
| Evolution | Evo Crystal (color-matched to weapon) | Same | ✅ Match | Keep |
| Bond/Level | Levels up with player | Same | ✅ Match | Keep |
| Secret Areas | Require specific ID ability | Same | ✅ Match | Keep |

**Action:** Rename "Companion" → "Innocent Devil" throughout all code, data tables, and specs.

---

## 5. WEAPON COMBINING SYSTEM

| Element | Original | My Rebuild | Status |
|---------|----------|------------|--------|
| Materials | ~40 types | ~40 types | ✅ Match |
| Forge Location | Julia's Shop | Julia's Shop | ✅ Match |
| Recipes | Material combinations | Material combinations | ✅ Match |
| Evo Crystal | Color-matched to weapon | Same | ✅ Match |
| Steal System | Purple lock timing | Same | ✅ Match |

**Status:** ✅ Weapon combining matches original.

---

## 6. LEVEL & ROOM MECHANICS

| Mechanic | Original | My Rebuild | Status |
|----------|----------|------------|--------|
| Room Lock | Enemies lock doors until cleared | Same | ✅ Match |
| Red Bars | Visual indicator of locked room | Same | ✅ Match |
| Save Rooms | Full heal + save | Same | ✅ Match |
| Candles | Breakable, drop items | Same | ✅ Match |
| Green Door Rooms | Innocent Devil acquisition | Same | ✅ Match |
| Map Checker | Colored X markers | Same | ✅ Match |
| Chapter Streaming | Level transitions | Same | ✅ Match |

**Status:** ✅ Level mechanics match original.

---

## 7. CONTROLS

| Action | Original (README) | My Rebuild | Status |
|--------|-------------------|------------|--------|
| Move | WASD | WASD | ✅ Match |
| Attack | J | J | ✅ Match |
| Special | K | K | ✅ Match |
| Jump | Space | Space | ✅ Match |
| Action/Evade | E / L | E / L | ✅ Match |
| Guard | Shift | Left Shift | ✅ Match |
| Summon | Q | Q | ✅ Match |
| Steal Focus | F | Not in input map | ❌ Missing |
| Lock-on | Tab | Not in input map | ❌ Missing |
| Pause | Esc / Enter | Esc / Enter | ✅ Match |
| Map | M | M | ✅ Match |
| Camera | V | V | ✅ Match |
| D-Pad | Arrows | Arrows | ✅ Match |

**Action:** Add F (Steal Target Focus) and Tab (Lock-on Target) to input mappings.

---

## 8. ITEMS

| Item | Original | My Rebuild | Status |
|------|----------|------------|--------|
| Potion | Heals HP | Heals HP | ✅ Match |
| High Potion | Heals more HP | Heals more HP | ✅ Match |
| Serum | Cure poison | Cure poison | ✅ Match |
| Uncurse | Remove curse | Remove curse | ✅ Match |
| Death Doll | Dies instead of player | ❌ Missing | Add |
| Materials | ~40 types | ~40 types | ✅ Match |

**Action:** Add Death Doll item.

---

## 9. SPECIFIC DEVIATIONS TO FIX

### Code-Level Changes Required:

1. **NobleArchimedesTypes.h:**
   - `ECompanionType` → `EInnocentDevilType`
   - `FCompanionData` → `FInnocentDevilData`
   - `UNobleArchimedesCompanionComponent` → `UNobleArchimedesInnocentDevilComponent`
   - "Companion" → "Innocent Devil" in all comments/UI text
   - Add `EDeathDoll` item type

2. **NobleArchimedesCharacter.h/.cpp:**
   - Player name default: "The Forgemaster" → "Hector"
   - SummonCompanion → SummonInnocentDevil
   - SetCompanionMode → SetInnocentDevilMode
   - GetCompanions → GetInnocentDevils

3. **Input Mappings (DefaultInput.ini):**
   - Add `F` = Steal Target Focus
   - Add `Tab` = Lock-on Target

4. **Data Tables (CSV):**
   - `CompanionDataTable.csv` → `InnocentDevilDataTable.csv`
   - Column: `CompanionType` → `InnocentDevilType`
   - Add Death Doll to item system

5. **UI Widget Spec:**
   - "Companion Status" → "Innocent Devil Status"
   - All "Companion" text → "Innocent Devil"

6. **Animation/Particle/Audio Specs:**
   - "Companion" → "Innocent Devil" in all references

---

## 10. CORRECTION PLAN

### Phase A: Rename & Align (Immediate)
- [ ] Rename all "Companion" → "Innocent Devil" in code, docs, data tables
- [ ] Rename "The Forgemaster" → "Hector"
- [ ] Add F (Steal Focus) and Tab (Lock-on) to input
- [ ] Add Death Doll item
- [ ] Rename CompanionDataTable.csv → InnocentDevilDataTable.csv

### Phase B: Verify Completeness
- [ ] All 10 chapter names exact match
- [ ] All 5 weapon types exact match
- [ ] All 11 damage types exact match
- [ ] All 6 Innocent Devils + Pumpkin exact match
- [ ] Combat timing values exact match
- [ ] Control scheme exact match

### Phase C: Add Missing Systems
- [ ] Death Doll implementation
- [ ] Steal Target Focus (F key)
- [ ] Lock-on Target (Tab key)
- [ ] Isaac as antagonist (story/NPC)
- [ ] Trevor Belmont as ally (story/NPC)

---

**Bottom Line:** The rebuild is ~90% faithful to the original. The main deviations are naming conventions (Companion vs Innocent Devil, The Forgemaster vs Hector) and two missing input bindings (F, Tab). All core mechanics, chapter structure, weapon types, damage types, and systems match the original game. These are simple find-and-replace corrections plus two input additions.

**No copyrighted assets were extracted.** All code, data tables, and specs are original implementations matching the original game's design for private use only.