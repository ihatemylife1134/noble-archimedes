# Research Findings: Castlevania: Curse of Darkness (PS2, SLUS-21168)
## For Private Educational Use Only — UE5 Fan Recreation Reference

**Source:** Disc image at `/Volumes/Untitled/FILEDATA.BIN` and related files
**Date analyzed:** 2026-10-19
**Status:** Format analysis only — no copyrighted assets extracted

---

## 1. Disc Layout

| Path | Size | Description |
|------|------|-------------|
| `SLUS_211.68` | 6,241,284 bytes | PS2 MIPS ELF boot executable |
| `FILEDATA.BIN` | 836,876,288 bytes | Game data archive |
| `SYSTEM.CNF` | ~80 bytes | Boot configuration |
| `IOP/` | 12 files | IOP processor modules |
| `PSS/` | 24 files, ~2.1 GB | Video cutscenes (MPEG2) |
| `SOUND/` | 2 files | Sound banks |

---

## 2. SLUS_211.68 — PS2 ELF Executable

**Format:** 32-bit MIPS ELF (ET_EXEC), little-endian

| Field | Value |
|-------|-------|
| Entry point | 0x00400008 |
| Machine | MIPS R3000 (0x08) |
| Program headers | 3 |

**Program Segments:**

| PH# | Type | VAddr | FileSz | MemSz | Flags |
|-----|------|-------|--------|-------|-------|
| 0 | Unknown (0x70000000) | 0x009326e0 | 0x18 | 0x18 | R |
| 1 | PT_LOAD | 0x00400000 | 0x005326f8 | 0x005326f8 | R+X |
| 2 | PT_LOAD | 0x00932700 | 0x000b356c | 0x002b2608 | W+R |

**Research notes for UE5 rebuild:**
- The MIPS executable contains all game logic: combat, AI, physics, inventory, companion AI
- No direct porting possible — must rewrite in C++/Blueprints
- Segment 1 (0x5.3 MB) is code + read-only data
- Segment 2 (~2.7 MB) is writable data + BSS (heap/stack)
- Entry point at 0x00400008 is the game's main startup

---

## 3. FILEDATA.BIN — Game Data Archive

**Header (offset 0x000):**
- Bytes 0x00-0x33: SYSTEM.CNF-style text: `BOOT2 = cdrom0:\SLPM_622.47;1` / `VER = 1.00` / `VMODE = NTSC`
- Bytes 0x34-0x7FF: Zero padding
- Offset 0x800: Directory table begins

**Directory Table (offset 0x800):**

| Field | Value |
|-------|-------|
| Magic | 0x82734927 |
| Unknown | 0 |
| Data start | 0x26000 (155,648 bytes) |
| Entry count | 11 |
| Entry size | 32 bytes |

**Entry format (32 bytes each):**
```
offset 0:  uint32  id
offset 4:  uint32  type
offset 8:  uint32  file_offset (relative to archive start)
offset 12: uint32  file_size
offset 16: uint32  unk4
offset 20: uint32  unk5
offset 24: uint32  unk6
offset 28: uint32  unk7
```

**Valid entries (entries 1-6):**

| Entry | ID | Type | Offset | Size | Likely purpose |
|-------|----|------|--------|------|----------------|
| 1 | 1 | 2 | 0x000000e0 | 0x00000280 | Small data file |
| 2 | 3 | 2 | 0x000107c0 | 0x00000880 | Small data file |
| 3 | 14539 | 0 | 0x000112a0 | 0x00003b08 | Type 0 (different category) |
| 4 | 14491 | 2 | 0x00015180 | 0x00000480 | Small data file |
| 5 | 14570 | 8 | 0x0001d660 | 0x00000370 | Type 8 |
| 6 | 14254 | 2 | 0x00025a40 | 0x00000480 | Small data file |

Entries 7-11 appear to be padding or invalid (zeroed or nonsensical values).

**File types found in archive data:**
- JPEG images (multiple, likely UI elements or texture pages)
- BMP images
- GZIP compressed data

**Research notes for UE5 rebuild:**
- The archive is a simple file bundle with offset/size table
- No encryption or complex compression on the directory
- Data starts at 0x26000 (aligned to 1536-byte boundary, likely CD sector size × 3)
- Images embedded in archive suggest UI textures, portraits, or item icons
- For UE5: Build your own archive system or use UE5's Pak file system

---

## 4. IOP/ — Input/Output Processor Modules

**12 IRX/IMG files** handle PS2 IOP-side processing:

| File | Size | Function |
|------|------|----------|
| CDVDSTM.IRX | 33,521 | CDVD stream module |
| IOPRP300.IMG | 275,921 | IOP runtime package |
| LIBSD.IRX | 30,085 | Library BD (sound) |
| LIBSMF2.IRX | 130,501 | SMF2 sound library |
| MCMAN.IRX | 130,501 | Memory card manager |
| MCSERV.IRX | 7,385 | Memory card server |
| MODSD.IRX | 107,693 | Module SD (sound driver) |
| PADMAN.IRX | 45,925 | Pad manager (controller input) |
| SDRDRV.IRX | 9,161 | SD reader driver |
| SDSTR3.IRX | 38,717 | SD stream 3 |
| SIO2MAN.IRX | 6,641 | Serial I/O manager |

**Research notes for UE5 rebuild:**
- UE5 has equivalent systems built-in: Audio engine, Input system, Save system
- No need to replicate IOP architecture — UE5 runs on a single CPU/GPU architecture
- Map IOP functions to UE5 subsystems:
  - PADMAN → Enhanced Input System
  - MCMAN/MCSERV → USaveGame / SaveGame system
  - LIBSD/MODSD → MetaSounds / Audio Engine
  - CDVDSTM/SDSTR → Asset streaming / Pak files

---

## 5. PSS/ — Video Cutscenes

**Format:** PS2 PSS (MPEG2 video + ADPCM audio in PS container)

**24 files, ~2.1 GB total:**

| File | Size | Chapter/Use |
|------|------|-------------|
| ST00_00.PSS | 82.4 MB | Chapter 1 - Abandoned Castle (opening) |
| ST01_00.PSS | 169.0 MB | Chapter 2 - Baljhet Mountains |
| ST02_00.PSS | 108.5 MB | Chapter 3 - Garibaldi Temple |
| ST03_00.PSS | 104.4 MB | Chapter 4 - Mortvia Aqueduct |
| ST04_00.PSS | 85.0 MB | Chapter 5 - Forest of Jigramunt |
| ST05T01.PSS | 64.3 MB | Chapter 5→6 transition |
| ST05_00.PSS | 16.1 MB | Chapter 6 - Cordova Town (part 1) |
| ST06_00.PSS | 88.1 MB | Chapter 6 - Cordova Town (part 2) |
| ST07_00.PSS | 65.6 MB | Chapter 7 - Eneomaos Machine Tower |
| ST08_00.PSS | 15.1 MB | Chapter 8 - Aiolon Ruins (part 1) |
| ST08_01.PSS | 137.2 MB | Chapter 8 - Aiolon Ruins (part 2) |
| ST09_00.PSS | 66.8 MB | Chapter 9 - Infinite Corridor (part 1) |
| ST09_01.PSS | 75.6 MB | Chapter 9 - Infinite Corridor (part 2) |
| ST10_00.PSS | 140.1 MB | Chapter 10 - Dracula's Castle (part 1) |
| ST11_00.PSS | 30.5 MB | Chapter 10 - Dracula's Castle (part 2) |
| ST11_01.PSS | 70.1 MB | Chapter 10 - Dracula's Castle (part 3) |
| ST12_00.PSS | 99.1 MB | Ending cutscene 1 |
| ST13_00.PSS | 97.9 MB | Ending cutscene 2 |
| ST14_00.PSS | 36.1 MB | Ending cutscene 3 |
| ST14_01.PSS | 136.0 MB | Ending cutscene 4 |
| ST15_00.PSS | 64.0 MB | Ending cutscene 5 |
| ST15_01.PSS | 179.2 MB | Ending cutscene 6 |
| ST16_00.PSS | 167.4 MB | Ending cutscene 7 |
| ST17_00N.PSS | 43.2 MB | Bonus/extra |

**PSS/EX/ subdirectory:**
- ST00R00.PSS (86.4 MB) — alternate/extended version of opening

**Research notes for UE5 rebuild:**
- PSS = MPEG2 video + ADPCM audio
- UE5: Use Media Player component with .mp4/.webm files
- Replace all 24 PSS cutscenes with original 2D/3D animated sequences
- For private recreation: Create original cutscenes using UE5 Sequencer

---

## 6. SOUND/ — Audio Banks

**SD.BIN (31,580,160 bytes):**
- Starts with `0x000001ba` = MPEG Program Stream start code
- Contains audio data in MPEG-PS format (likely VAG/ADPCM wrapped in PS)
- Header table at offset 0x00 with entry sizes

**SD_NTSC.BIN (282,611,712 bytes):**
- Sound bank index + data
- Starts with offset table (pairs of offset/size values)
- Contains 100s of individual sound entries

**Sound bank table format (SD_NTSC.BIN offset 0x00):**
```
Each entry: uint32 offset, uint32 size
Entry 0: offset=0x00000067, size=0x00000001
Entry 1: offset=0x00d0ae20, size=0x00001a17
...
```

**Research notes for UE5 rebuild:**
- PS2 used VAG (ADPCM) audio format
- UE5: Use .wav/.ogg files imported via Sound Cue / MetaSounds
- Build your own sound bank system using UE5's Audio Engine
- Map sound categories: footsteps, combat hits, weapon swings, magic, UI, ambient

---

## 7. Game Systems to Rebuild in UE5

Based on the disc structure and Bradygames guide, the following systems must be implemented:

### 7.1 Combat System
| Original | UE5 Equivalent |
|----------|---------------|
| Two-button attack (J/K or X/Y) | Enhanced Input actions |
| Combo chains (3 stages) | Combo state machine in C++ |
| Final attack timing | Timing window checks |
| Guard (hold) | Input hold detection |
| Perfect Guard (0.1s release window) | Frame-perfect timing check |
| Quick Step (0.3s invulnerability) | Invulnerability frames + dodge roll |
| Double Step | Double-tap detection |
| 5 weapon types | Weapon enum + animation montages |
| 11 damage types | Damage type enum with weakness matrix |

### 7.2 Innocent Devil (Companion) System
| Original | UE5 Equivalent |
|----------|---------------|
| 6 companions + Pumpkin | Companion actor classes |
| Auto/Command/Guard modes | AI behavior enum |
| Evo Crystal evolution | Evolution state machine |
| Bond/level system | Experience + level variables |
| Secret area access | Ability-gated level design |

### 7.3 Weapon Combining System
| Original | UE5 Equivalent |
|----------|---------------|
| ~40 materials | Material data table |
| Forge at Julia's shop | Crafting UI widget |
| Recipes (materials → weapon) | Data table of recipes |
| Steal system (purple lock) | Steal timing minigame |

### 7.4 Level Structure
| Original | UE5 Equivalent |
|----------|---------------|
| 10 chapters | 10 streaming levels |
| Room lock (red bars) | Door/barrier actors with enemy count |
| Save rooms (full heal) | Save point actors |
| Candles (breakable items) | Destructible actors with loot |
| Map Checker (colored X) | Map widget with markers |
| Green door rooms | Companion acquisition triggers |

---

## 8. UE5 Implementation Roadmap

### Phase 1: Core Engine Setup
- Create UE5 C++ project (Third Person template)
- Set up Enhanced Input with 12 actions
- Implement character controller with movement
- Set up Git LFS for binary assets

### Phase 2: Combat System
- Attack state machine (idle → light ×3 → heavy → idle)
- Perfect Guard timing (0.1s window)
- Quick Step with invulnerability frames
- 5 weapon types with unique animations
- 11 damage types with weakness/tolerance matrix

### Phase 3: Companion System
- 6 companion classes + Pumpkin
- Auto/Command/Guard AI modes
- Evo Crystal evolution system
- Companion leveling

### Phase 4: Levels & Streaming
- 10 chapter levels with level streaming
- Room lock system
- Save rooms with auto-save
- Candle breakable objects
- Chapter transitions

### Phase 5: Systems
- Weapon combining/forge
- Steal system
- Inventory management
- Save/load (5 slots + auto)
- UI/HUD (health, mana, combo, companion status)

### Phase 6: Audio & VFX
- MetaSounds for combat audio
- Sound cues for UI, footsteps, ambient
- Niagara VFX for weapon trails, hits, magic
- Original music composition

### Phase 7: Polish & Playtest
- Full playthrough Chapter 1 → Chapter 10
- Bug fixing and balance
- Performance optimization (60 FPS target)

---

## 9. What Was NOT Extracted (Copyright Compliance)

The following copyrighted content was **identified but not extracted**:
- ❌ SLUS_211.68 executable code (MIPS machine code)
- ❌ FILEDATA.BIN archive contents (textures, models, data)
- ❌ PSS video cutscenes (MPEG2 video)
- ❌ SOUND banks (VAG/ADPCM audio)
- ❌ IOP modules (PS2 system software)

**All game logic, assets, audio, and video must be recreated originally in UE5.**

---

## 10. Session Handoff

When resuming work on the Windows GPU machine:
1. Review `SESSION_HANDOFF.md` for git state and agent configuration
2. Review this document (`RESEARCH_FINDINGS.md`) for format specifications
3. Create UE5 project at `C:\Projects\NobleArchimedes\`
4. Implement systems per Phase 1-8 roadmap
5. Build playtest build for private use only

---

**Private educational use only. Do not distribute or monetize.**