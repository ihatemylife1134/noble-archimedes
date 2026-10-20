# Noble Archimedes — Completion Plan

Fan recreation of *Castlevania: Curse of Darkness* for **private use** in Unreal Engine 5.8.
No copyrighted assets, ISOs, ELF dumps, or extracted content are stored in this repository.

## Ground rules

- `UE5_Source/` is the single source of truth. Changes are authored there, then synced to the
  active project at `C:\Projects\NobleArchimedes\`.
- The build must genuinely run in Unreal Editor. No functionality is disabled to fake success.
- Every phase ends with a **QA gate**: build must be green and the phase checks must pass before
  moving on.
- Fidelity is measured against the written specs (`Content/Blueprints/*.md`) and the CSV data
  tables, since the original disc data is intentionally not in the repo.

## QA gates (run at the end of every phase)

| Check | Command | Pass criteria |
|-------|---------|---------------|
| Compile | `Build.bat NobleArchimedesEditor Win64 Development -Project=...` | `Result: Succeeded` |
| Data tables | `python Tools/validate_data_tables.py` | 0 errors |
| Fidelity | `python Tools/validate_rebuild_fidelity.py` | 0 errors |
| Completeness | `python Tools/check_rebuild_completeness.py` | no missing required files |
| Assets (in-editor) | `UnrealEditor-Cmd.exe ... -run=PythonScript -script=Tools/ue5_verify_content.py` | 0 errors |
| Repo clean | `python UE5_Source/Tools/check_clean_repo.py` | no build artifacts / disallowed content |

## Phases

### Phase 0 — Baseline (DONE)
- 23 C++ classes compile clean.
- Editor launches, module initializes, startup map loads.
- Build scripts build before launching.

### Phase 1 — Data & class layer (DONE)
Deliverables:
1. Struct fields aligned with the CSV schemas (weapon animation counts, ID evolution
   crystal, chapter room counts).
2. 11 Data Tables imported from `Content/DataTables/*.csv`.
3. Core Blueprints created from the C++ classes.
4. Enhanced Input assets (`IA_*`) + `IMC_Default`.
5. C++ Enhanced Input wiring on `AHectorCharacter` (was missing entirely).
6. GameMode / GameInstance / default pawn / HUD wired in project settings.
7. Level blockout of Chapter 1 with 4 rooms, lights, PlayerStart, spawns.

Acceptance: PIE starts, Hector is possessable, WASD/look/attack respond, Data Tables open
without import errors, level contains the four Chapter 1 rooms.

Verified: compile green, 11 tables imported, 27 input mappings, 4 room instances,
HUD widget layout builds at runtime, game smoke test reaches Hector BeginPlay with
zero errors. Note: enemy archetypes still use the placeholder cube mesh until the
presentation phase; recipes now cover all 19 weapons.

### Phase 2 — Combat & systems parity
- Combo chain, guard/perfect guard, quick step i-frames driven by the data tables.
- Weapon forge: recipes, materials, forging currency.
- Item drops / stealing from enemy data.
- Innocent Devil summon, modes, evolution.
- Save/load across the 6 slots + autosave.

### Phase 3 — Chapters 2–10
- Data-driven encounter spawning (room reads `EnemyEncounterTable`).
- 10 chapters/areas with room templates and boss arenas.
- Progression gating from `ChapterProgressionTable`.

### Phase 4 — Presentation
- Animation Blueprints + montages for Hector/enemies/bosses.
- Materials from `MaterialDataTable`, Niagara VFX, audio cues from `AudioSpec`.
- UMG: HUD, pause, save/load, main menu, map.

### Phase 5 — AI
- Behaviour trees/blackboards for enemy archetypes, boss phase logic.

### Phase 6 — Packaging
- Shipping cook + package, smoke test the packaged build, performance pass.

## Progress log

| Date | Phase | Notes |
|------|-------|-------|
| 2026-10 | 0 | Build green, editor verified |
| 2026-10 | 1 | Struct fields aligned; input wiring added |
| 2026-10 | 1 | 11 DataTables, 27 mappings, 4-room Chapter 1 blockout, HUD layout, QA gate green |
| 2026-10 | 2 | Started: evolution-crystal data model corrected; recipe coverage completed |
