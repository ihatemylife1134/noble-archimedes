# SESSION HANDOFF — Noble Archimedes: Castlevania: Curse of Darkness UE5 Fan Recreation

## Project Status
**Phase 1–4 planning complete.** Code changes committed to local git. Ready for UE5 project creation on Windows GPU machine.

## Repository Location
`/Users/matthewjohnson/Documents/GitHub/noble-archimedes`

## Git Status (as of last session)
- Branch: `master`
- Remote: `origin` → `https://github.com/ihatemylife1134/noble-archimedes.git` (private repo)
- Upstream: `https://github.com/sergiomanzur/noble-archimedes.git` (original recomp project)
- Last commit: `72ee6d6` — "Stage A EE scheduler optimizations + agent team + VU backend default fix"
- All changes committed locally. **PUSH FAILED** — GitHub credentials not configured in this headless environment. Need to run `git push origin master` on a machine with GitHub auth (or set up credential helper/PAT).

## What Was Built (Existing Recomp Project — Noble Archimedes PS2 Recompilation)
This is the **source project** being recreated in UE5:
- PS2 MIPS→C++ recompilation of Castlevania: Curse of Darkness (SLUS-21168)
- Runtime: EE scheduler, VIF1 worker, generic VU, GS backends (paraLLEl-GS, PCSX2 GS hybrid)
- Tools: chunk generation, stub registry, sound bank compat, link scripts
- Location: `tools/PS2Recomp/` (submodule, pinned at `75d729ce`)
- Patches applied: `tools/patch_stage_a_v2_scheduler.py` (Stage A scheduler: fast block cache, pacing deadline, quantum budget)

## Files Modified in This Session
1. `release/windows/Launch Native.cmd` — Removed `PS2_VU_BACKEND=play` default (was a release blocker requiring unsupplied module). Generic VU now default.
2. `release/windows/README-WINDOWS.txt` — Added VU BACKEND documentation section.
3. `src/main.cpp` — Removed `PS2_VU_BACKEND=play` default from `configureDefaultNativeRuntimeOptions()`. Now consistent with launcher.
4. `tools/patch_stage_a_v2_scheduler.py` — Fixed broken anchors for this codebase version:
   - Removed `nobleDmacCompletionPending()` (undefined in codebase)
   - Changed `anchor_budget` from `HostProfile::maybeReport` to `PS2Runtime::RecompiledFunction function = m_runtime.lookupFunction(context.pc);`
   - Removed `HostProfile::Scope loopProfileScope` from `old_loop_entry`
   - Updated `old_due_pacing` to match actual `m_eventCv.wait_until` block
5. `tools/PS2Recomp/ps2xRuntime/src/lib/Kernel/EeScheduler.cpp` — Applied all 7 Stage A patch steps:
   - FastBlockCacheSlot[65536] L1 cache + fastLookupBlock() + s_pacingDeadline
   - Cache + deadline reset in EeScheduler::reset()
   - computeSafeQuantumBudget() lambda (2048-cycle inner quantum)
   - s_pacingDeadline pacing check before processPendingEvents()
   - Record s_pacingDeadline in processDueDeadlines() when host-future
   - Clear s_pacingDeadline when due events drained
   - Non-stalling updateNextDeadline() with future-deadline awareness
6. `.gitignore` — Added `.DS_Store` exclusion.
7. `.opencode/agents/` — 16 subagent definitions created (director + 15 specialists).
8. `.opencode/opencode.jsonc` — Director set as default agent.

## Phase 1–4 Planning Complete (Documented in Conversation)
All four phases have been fully designed with subagent-level detail:

### Phase 1: Core Systems
- Combat: 2-button attacks (light + final), combo timing windows, Perfect Guard (0.1s), Quick Step (0.3s i-frames)
- 5 weapon types: Sword, Axe, Spear, Knuckles, Special
- 11 damage types: Fire, Ice, Light, Dark, Poison, Curse, Paralyze, Stone, Slash, Blunt, Magic
- Camera: Classic (4.2 UU, 70°), Action Orbit (3.6 UU, 78°), Over-the-Shoulder (1.75 UU, 65°)
- Input: Enhanced Input, keyboard + gamepad
- Save: 5 manual slots + 1 auto-save, save rooms fully heal

### Phase 2: World & Levels
- 10 chapters from Bradygames guide: Abandoned Castle, Baljhet Mountains, Garibaldi Temple, Mortvia Aqueduct, Forest of Jigramunt, Cordova Town, Eneomaos Machine Tower, Aiolon Ruins, Infinite Corridor, Dracula's Castle
- Level streaming between chapters
- Room lock mechanics (enemies lock doors until cleared)
- Save rooms, candles (breakable), green door rooms (companion acquisition)
- Enemy AI from bestiary (11 damage types, weakness/tolerance pairs)
- Innocent Devils: 6 types + Pumpkin, Auto/Command/Guard modes, Evo Crystal evolution
- Weapon combining: ~40 materials

### Phase 3: Fan Recreation Completion
- All gameplay systems integrated
- Full save/load across chapters
- Audio: combat, ambient, UI, companion
- VFX: weapon trails, perfect guard flash, hit sparks
- UI/HUD: health, mana, combo, companion status, minimap

### Phase 4: Content Production (Playtest Ready)
- Complete asset list: player model, enemies, bosses, companions, weapons, items, environments
- Animation requirements per character type
- Material shader specifications
- Chapter-by-chapter environment build list
- QA playtest plan (beginning to end)
- Build/packaging script for Windows Shipping build

## Bradygames Guide Reference (Public, Used for Design Only)
URL: `https://archive.org/stream/CastlevaniaCurseOfDarknessBradygames/Castlevania%20-%20Curse%20of%20Darkness%20%28Bradygames%29_djvu.txt`
- 28,388 lines — contains chapter layouts, enemy data, weapon types, damage types, innocent devil system, weapon combining recipes, steal mechanics, save room rules
- Used as design reference only (public text, not game assets)

## Archive.org ISO Reference (NOT downloaded, NOT processed)
URL: `https://archive.org/download/castlevania-curse-of-darkness_202206`
- Contains `Castlevania - Curse of Darkness.chd` (2.8GB) + cover images
- **Not downloaded or processed** — copyrighted game content
- Not needed for UE5 recreation (built from guide + original design)

## Legal/IP Status
- **Excluded from future phases per user instruction** — will not revisit until user explicitly says original rebuild is complete
- Fan recreation for private use only, no distribution, no monetization
- Original names used ("The Forgemaster" not "Hector", companions not "Innocent Devils" in public-facing docs)
- All code and assets are original creations inspired by original game design

## Docker Desktop
- Installed at `/Applications/Docker.app`
- CLI at `/Applications/Docker.app/Contents/Resources/bin/docker`
- Docker Engine v29.9.1 running
- Add to PATH: `export PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH"`
- Not yet used for Windows GPU access

## OpenCode Agent Team (`.opencode/agents/`)
16 agents configured for future session use:
- `director` (primary) — orchestrates all phases
- `studio/leads/recomp-lead` — recompilation, runtime, scheduling, VU/GS
- `studio/engineering/pc-port-engineer` — Windows x64 toolchain, CMake/Ninja
- `studio/engineering/rendering-engineer` — Vulkan/paraLLEl-GS, PCSX2 GS hybrid
- `studio/engineering/audio-engineer` — VAG decoding, sound banks, host audio
- `studio/engineering/input-platform-engineer` — input mapping, platform services
- `studio/engineering/vfs-storage-engineer` — VFS, ISO extraction, saves
- `studio/engineering/performance-engineer` — profiling, frame pacing, benchmarks
- `studio/quality/qa-test-engineer` — test strategy, gameplay validation
- `studio/compliance/legal-ip-compliance` — copyright, clean-room, licensing (EXCLUDED until user says otherwise)
- `studio/creative/clean-room-design-director` — original IP design
- `studio/creative/asset-replacement-artist` — original assets/audio/UI
- `studio/ops/build-release-engineer` — packaging, alpha releases, sanitization
- `studio/ops/docs-technical-writer` — documentation, build instructions
- `studio/ops/data-pipeline-engineer` — build scripts, code generators, automation

## Next Steps (When Windows GPU Machine Accessible)

### Immediate (Session 2)
1. **Configure GitHub credentials** so `git push origin master` works
2. **Install Unreal Engine 5.5+** on Windows GPU machine (Epic Games Launcher)
3. **Create UE5 C++ project**: `NobleArchimedes` at `C:\Projects\NobleArchimedes\`
4. **Copy agent team** to project: `.opencode/agents/` folder
5. **Create C++ classes** (Phase 2 list above)
6. **Set up Enhanced Input** with all 12 actions
7. **Begin Chapter 1 blockout** (Abandoned Castle)

### UE5 Project Structure to Create
```
C:\Projects\NobleArchimedes\
├── .opencode\agents\          (copy from this session)
├── .gitignore                 (UE5 + LFS rules)
├── .gitattributes             (LFS tracking for .uasset, .umap, etc.)
├── NobleArchimedes.uproject
├── Config\
├── Content\
│   ├── Blueprints/
│   ├── Maps/
│   │   ├── PersistentLevel.umap
│   │   └── Chap_01_... through Chap_10_...
│   ├── Models/, Textures/, Materials/, Animations/
│   ├── Audio/SFX/, Music/, Ambient/, UI/
│   └── VFX/
├── Source/
│   └── NobleArchimedes/
│       ├── Public/  (10 header files)
│       └── Private/ (10 cpp files)
├── Tools/
│   ├── build_ue5.bat
│   ├── package_playtest.bat
│   ├── validate_content.py
│   └── chapter_transition.py
├── Docs/
│   ├── PHASE_1_PLAN.md through PHASE_4_PLAN.md
│   ├── COMBAT_SYSTEM.md
│   ├── WEAPON_SYSTEM.md
│   ├── COMPANION_SYSTEM.md
│   ├── LEVEL_DESIGN.md
│   ├── ENEMY_BESTIARY.md
│   ├── CONTROLS.md
│   └── PLAYTEST_GUIDE.md
└── SESSION_HANDOFF.md  (this file)
```

### Build Command (Windows PowerShell)
```powershell
# Create project
.\Engine\Binaries\Win64\UnrealEditor.exe -projectfile="C:\Projects\NobleArchimedes\NobleArchimedes.uproject" -game

# Build
UnrealEditor.exe NobleArchimedes -run=Build -target=NobleArchimedes -platform=Win64 -configuration=Development

# Package
RunUAT.bat BuildCookRun -project=... -platform=Win64 -clientconfig=Shipping -serverconfig=Shipping -cook -stage -package -prerequisites -build
```

## Git Push Credentials Issue
`git push origin master` failed with "Device not configured" — no GitHub credentials cached in this environment. On the Windows machine or any machine with GitHub access:
1. Run `git config --global credential.helper manager` (or store)
2. Run `git push origin master` from `/Users/matthewjohnson/Documents/GitHub/noble-archimedes`
3. Or use a Personal Access Token (PAT) for HTTPS auth

## Key Design Decisions (Do Not Re-litigate)
- Unreal Engine 5 for the rebuild (not continuing the PS2 recomp)
- Fan recreation of Castlevania: Curse of Darkness, private use only
- Original names/assets/code (clean room, no extracted game content)
- 10 chapters matching Bradygames guide structure
- 5 weapon types, 11 damage types, 6 companions + Pumpkin
- Perfect Guard (0.1s), Quick Step (0.3s i-frames), Double Step
- Level streaming between chapters
- Save rooms fully heal + auto-save
- Legal/IP compliance excluded until user explicitly re-enables

## Session Handoff Complete
All planning documentation exists in the conversation history. This SESSION_HANDOFF.md is the single source of truth for resuming work. The local git repo has all code changes committed and ready to push once credentials are configured.