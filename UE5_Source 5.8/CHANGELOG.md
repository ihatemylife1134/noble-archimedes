# Changelog - UE5 Chapter 1 rebuild


## 2026-10-22 (cont.) — Hector swapped onto the new mesh with a working animation graph

### Retargeted clips were never reaching disk

Both retarget batches reported success and produced nothing. `duplicate_and_retarget`
creates assets **in memory only**: the folder `/Game/Characters/HectorBase/Retargeted`
did not exist on disk at all, so `AB_HectorBase` found no clips to play. Added an
explicit `save_directory(OUT_DIR, recursive=True)` after the batch operation, which
now reports `True`, and the 12 procedural clips are on disk.

This is the second time this trap has bitten: the earlier instance was the imported
`survival_character_Skeleton` never being saved, which produced *"Unable to retrieve
target USkeleton"* while every in-session check passed. Commandlet-created assets
must always be saved explicitly.

### `AB_HectorBase` built on `survival_character_Skeleton`

| Item | Value |
| --- | --- |
| States | `Idle`, `Walk`, `Run` |
| Transitions | 4 — `bIsMoving`, `bIsRunning`, `bIsIdle`, `bIsIdle` |
| Blend times | 0.1s, per `AnimationBlueprintSpec.md` |
| Variables | `bIsMoving`, `bIsRunning`, `bIsIdle` (the exact names `AnimVariableBridge` writes) |
| Entry / root / pose | connected / connected / contributing |
| Compiled | yes |

The clip candidates fall back to the procedural `RTG_AN_Hector_*` set, because the
five **mocap** clips (`RTG_anim_Idle`, `Walk_Fwd_Loop_L/_R`, `Jog_Loop_Fwd/_Bwd`) are
still absent from disk — that earlier batch hit the same unsaved-asset bug. They
need re-running to get mocap rather than the procedural placeholder animation.

### The missing slot node

A factory-created `AnimBlueprint` has no **slot** node. `ConnectStateMachineToSlot`
searches for one, finds none, and returns false — leaving the state machine wired
straight to the Root. Since montages override a **slot** and not the Root, the
locomotion pose would animate while attacks stayed invisible.

Added three functions to `NobleAnimGraphAuthoring`:

- `EnsureSlotNode(AnimBlueprint, SlotName)` — returns the slot node, creating it
  with the same construction sequence the editor's "Add Slot" action uses
  (`NewObject` → `AddNode` → `CreateNewGuid` → `PostPlacedNewNode` → set
  `Node.SlotName` → `AllocateDefaultPins`).
- `GetSlotName(AnimBlueprint)` — reports the existing slot's name.
- `EnsureSlotPipeline(AnimBlueprint, StateMachine, SlotName)` — wires
  machine → slot → root in one call.

The slot name is **read from the existing `AB_Hector`** (`DefaultSlot`) rather than
guessed, so the montages already built against that name keep working.

Result: `ensure_slot_pipeline = True`, root connected, machine contributing,
compiled.

### Player mesh swapped

`BP_HectorCharacter`'s mesh component now points at the new character:

```
mesh before = /Game/Characters/Hector/SK_Hector.SK_Hector
mesh after  = /Game/Characters/HectorBase/SK_HectorBase.SK_HectorBase
anim class  = AB_HectorBase_C
```

Editing the component archetype on the Blueprint's CDO and saving the Blueprint
persists the change — the archetype *is* the Blueprint's component template.

### New tools

- `Tools/retarget_attacks.py` — stub rig → new rig, with the save fix.
- `Tools/build_ab_hectorbase.py` — creates the AnimBlueprint, states, transitions,
  variables, slot pipeline, and performs the mesh swap.
- `Tools/fix_ab_base_slot.py` — applies the slot pipeline and reports state.
- `Tools/diag_ab_base.py` — dumps the anim graph for diagnosis.
- `Tools/blender_open_character.py`, `Tools/dump_gasp_camera.py` — inspection aids.

### Game Animation Sample reviewed (not integrated)

Fab's **Game Animation Sample** (5.8, 7.1 GB) was downloaded. Its camera is UE 5.8's
data-driven **Camera Rig** system — `CameraRigAsset` assets (`Close`/`Medium`/`Far` ×
`Aim`/`Freecam`/`Strafe`), a `CameraAsset`, a `CameraDirector` and a `ChooserTable`
for runtime selection — not a spring arm with hard-coded numbers. `CameraRigAsset`
exposes **no reflected properties to Python**, so its values could not be read out
for comparison; adopting it would also mean taking on the `Chooser` plugin and a
different camera architecture from our C++ `CameraBoom`.

Its locomotion is motion matching (PoseSearch + Chooser + AnimationWarping), whereas
`AnimationBlueprintSpec.md` specifies a state machine plus a `BS_Locomotion` blend
space. The state machine we built is therefore the spec-compliant choice; GASP's
value was the camera architecture as a reference, not a drop-in.

---

## 2026-10-22 (cont.) — Removed the pre-5.8 source tree; single tree remains

The repository carried two copies of the project source: the current
`UE5_Source 5.8/` and a stale pre-5.8 `UE5_Source/`. The old tree is gone.

### What was removed

- `UE5_Source/` — 128 files, 663 KB, plus the one binary it held
  (`Content/Maps/Chap_01_AbandonedCastle.umap`). All 11 chapter maps remain in
  the active tree.
- **26 of its documents were byte-identical duplicates** of the 5.8 tree, so the
  only content lost was four stale docs and two superseded scripts:
  - `AI_PASSOFF.md` — declared the project "not ready for a direct compile" with
    P0 blockers (invalid `Build.cs` syntax, missing `Target.cs`, missing
    SaveGame implementation). All long fixed.
  - `CONVERSATION_CONTEXT.md` — declared "all engineering work complete" and
    referenced files that no longer exist (`SESSION_HANDOFF.md`,
    `opencode.jsonc`). Directly contradicts `AI_PASSOFF.md` in the same folder.
  - `TRANSFER_GUIDE.md` — described copying sources into a fresh Third Person
    template by hand, a workflow superseded by the scripted content pipeline.
  - `PROJECT_PLAN.md` — phase plan and QA-gate table; superseded by `CHANGELOG.md`
    as the progress record.
  - `Tools/ue5_create_blueprints.py`, `Tools/ue5_import_datatables.py` —
    superseded by `ue5_build_content.py`.

  All six remain recoverable from git history if ever needed.

### Path references repointed

Eleven files referenced the old tree by path and now point at `UE5_Source 5.8/`:
`check_clean_repo.py`, `check_project_readiness.py`, `convert_csv_to_datatable.py`,
`generate_localization.py`, `generate_ue5_import_manifest.py`,
`generate_ue5_project_structure.py`, `build_asset_manifest.py`,
`validate_data_tables.py`, `ue5_implementation_checklist.md`, `UE5_BUILD_GUIDE.md`
and `Content/DataTables/README_DataTables.md`.

Two of these were hard-coded path roots that would have resolved to nothing:
`check_project_readiness.py` had `PROJECT_ROOT = Path("UE5_Source")` and
`convert_csv_to_datatable.py` had `DATA_TABLES_DIR = Path("UE5_Source/Content/DataTables")`.

### A quiet bug this exposed

`check_clean_repo.py` resolves `ROOT` to the repository root, but its
`ALLOWED_BINARY_PATHS` and forbidden-directory lists named `UE5_Source/...` — the
**old** tree. So the repository-cleanliness gate had been inspecting a tree that
was not the active project. It now names `UE5_Source 5.8/...` and checks the tree
that actually exists.

### Still outstanding

- `.github/workflows/windows-build.yml` lives inside the project tree rather than
  at the repository root. GitHub only reads workflows from `<repo>/.github/workflows`,
  so CI has never run.

---

## 2026-10-22 (cont.) — New player character imported, retarget pipeline unblocked, camera retuned

### The retarget blocker from the previous entry is resolved

The earlier session concluded an `IKRigDefinition` could not be given a skeletal
mesh, so auto-chains never generated. That was wrong. `set_editor_property(
"preview_skeletal_mesh", mesh)` works fine — `get_editor_property` throws on that
property, and the throw was mistaken for the setter being unsupported. With the
mesh set, `apply_auto_generated_retarget_definition()` populates bones and chains
normally.

Second, subtler failure: an asset created by a commandlet lives in memory until
explicitly saved. The imported Skeleton was never persisted, so the retargeter
reported *"Unable to retrieve target USkeleton"* while every in-session check
passed. Every created asset now goes through `save_asset` / `save_directory`.

### `SK_HectorBase`: the real player character

- `survival_character.fbx` (9 MB) imported to
  `/Game/Characters/HectorBase/`: 11 skinned parts, one 160-bone armature.
- Measured **1.88 m** tall, eyes at 1.73 m — correct human scale, no 100× unit
  surprise. Stands upright, faces **−Y** in Blender (to be confirmed in-engine).
- **Bone names are UE-mannequin naming, not Mixamo.** Mannequin vs new character
  shares **45 bones with 0 new-only**; old stub `SK_Hector` vs new shares only 13.
  That is why the retarget maps 29→29 instead of the lossy 29→9 the stub gave.
- `IKRig_HectorBase` built with 29 chains, `RTG_HectorBase` retargeter against the
  mannequin.

### Clips on the new skeleton

| Source | Result |
| --- | --- |
| Mocap (mannequin) → new character | `RTG_anim_Idle`, `Walk_Fwd_Loop_L/_R`, `Jog_Loop_Fwd/_Bwd` |
| Procedural `AN_Hector_*` (stub) → new character | 12 clips: Idle, Walk, Run, Light1–3, Heavy, Guard, QuickStep, Jump, HitReaction, Death |

The procedural pass matters: attack montages are bound to the old stub skeleton,
so swapping the mesh without it would have silently broken combat. A second
retargeter `RTG_StubToBase` (stub rig → new rig) carried all 12 across through
the 13 shared bone names.

`Tools/retarget_attacks.py` does this batch; `Tools/retarget_to_base.py` builds
the rig and retargeter.

### Camera retuned toward a modern over-the-shoulder rig

No numeric camera spec exists anywhere in the project docs — only the
`ECameraMode` enum, the spring arm and a note that modes must drive the boom. The
reference therefore came from the engine's own free `TP_ThirdPerson` template,
whose `CombatCharacter` uses a 100 cm boom (pulling to 400 for death), with both
position and rotation lag enabled.

| Mode | Before | After |
| --- | --- | --- |
| Classic | arm 350, offset (0,0,70), FOV 90 | **arm 300, offset (0,50,75), FOV 90** |
| ActionOrbit | arm 450, offset (0,0,110), FOV 80 | **arm 420, offset (0,0,120), FOV 85** |
| OverTheShoulder | arm 250, offset (0,60,90), FOV 75 | **arm 180, offset (0,70,80), FOV 80** |

- **Camera lag added** (`CameraLagSpeed` 10, `CameraRotationLagSpeed` 12). Its
  absence is why the follow felt rigid: the boom snapped to the character instead
  of trailing it.
- **Shoulder bias** (`SocketOffset.Y` 50) so the character sits off-centre rather
  than dead-centre. Y was 0 in every mode before.
- `bDoCollisionTest` left **off** on purpose; the probe jammed the boom against
  walls and lock barriers in the tight blockout. Revisit once rooms have real
  collision.
- **Pitch clamp added** in `ANobleArchimedesPlayerController::BeginPlay`:
  `ViewPitchMin = -60`, `ViewPitchMax = 40`. There was none, so the view could be
  tipped straight up or down.

### Tooling lessons

- **`--no-splash` is not a valid Blender 4.5 flag.** Blender parsed it as a
  filename, failed with *"cannot read file .../--no-splash"* and exited — which
  looked exactly like the import script crashing on startup.
- `bpy.ops.wm.read_factory_settings()` inside a `-P` script reinitialises Blender
  mid-launch and must not be used to open a file; delete the default objects
  instead.
- `Start-Process -ArgumentList` does not quote arguments, and flags must be valid
  or they are consumed as paths.

### Still open

- `AB_Hector` remains bound to the stub skeleton, so the new mesh needs
  `AB_HectorBase`; no anim blueprint exists for it yet.
- `BP_HectorCharacter` still points at the old mesh.
- 4K UDIM textures (~250 MB) not imported or downscaled.

---

## 2026-10-22 (cont.) — Fab content integration: animation library and sword audio

### Packs reviewed

- **Free Animation Library** (Fab, 189 MB, 517 files) copied to
  `Content/FreeAnimationLibrary`. Covers Idle, Walk, Jog, Jump, FallLoop,
  LandingRoll, Slide, Vault, Mantle, LedgeClimb, Crouch, Swim, Ladder and more.
  It must sit at the pack's own content root: copying it under
  `Content/Fab/FreeAnimationLibrary` broke every clip, because animation assets
  resolve their skeleton by absolute `/Game/FreeAnimationLibrary/...` path. The
  failure surfaced as "Unable to retrieve target USkeleton".
- **Free Spells** VFX (471 MB) and **Procedural Building Generator** (682 MB) are
  downloaded and available, not yet integrated.
- **Sword SFX pack**: 30 wav in four categories imported to
  `/Game/Audio/SFX/Sword/{SwordAttack,SwordSwoosh,SwordUnsheathe,SwordSharpening}`
  via `Tools/import_audio.py`. Wired into combat: swoosh plays when a light or
  heavy attack starts, impact plays when a hit lands on an enemy. Sounds are
  resolved once per session and skipped silently if missing.
- **8 roll FBX** (`RM_Roll_*`, eight directions) extracted, not yet imported.
- `replacements.zip` (6.4 GB, 5033 hashed PNGs) is unidentified and was left
  untouched rather than guessed into the project.

### Retargeting API: scriptable, one blocker

Confirmed available: `IKRigDefinitionFactory`, `IKRetargetFactory`,
`IKRetargetBatchOperation.run_batch_retarget`, `IKRetargeterController`,
`IKRigController`, plus ops for stride warping, floor constraint and speed
planting. Actual signatures differ from the obvious guesses:

| Call | Real signature |
| --- | --- |
| `set_ik_rig` | second argument is `RetargetSourceOrTarget` enum, not a bool |
| `auto_map_chains` | `(auto_map_type, force_remap)` |
| `run_op_initial_setup` | `(op_index)` |
| batch inputs | `assets_to_retarget` needs `AssetData`, not `AnimSequence` |

Blocker: no scriptable way to give an `IKRigDefinition` its skeletal mesh
(`set_preview_mesh` exists on `IKRetargeterController`, not `IKRigController`), so
`apply_auto_generated_retarget_definition()` returns `ok=False, count=0` and there
are no chains to map. Separately, `.../Meshes/SK_Mannequin` loads as a **Skeleton**,
not a SkeletalMesh, which the batch operation rejects.

---


## 2026-10-22 (cont.) — Arms rest at the sides: axes derived from the rig

- Three attempts failed because the axes were guessed. `hector_rig.py` defines the
  rig as **Z up, −Y forward, +X = character's left, roll = 0 on every bone**, and
  Blender aligns a roll-0 bone's local Z to world up. For `upperarm_l` (head
  16,0,147 → tail 44,0,147, along +X) that gives local X = world −Y, local Y along
  the bone, local Z = world +Z; for `upperarm_r` (along −X) local X = world +Y.
- The mapping is therefore: **local X raises/lowers the arm, local Z sweeps it
  forward/back, local Y is twist.** The original code used Z for the drop (so the
  arms swept forward) and X for the swing (so nothing moved vertically). The
  62° and 80° Y attempts rotated about the twist axis, which is why the arms never
  lowered no matter the angle.
- Fix: both upper arms drop on **local X at −78°** — the same sign on each side
  because left local X is world −Y and right is world +Y, so the sign cancels —
  with lower arms at −8°. Walk and run swing moved to **local Z with mirrored
  signs**.
- Confirmed by playtest: arms rest at the sides standing still and while walking.
- Still using the old swapped convention, so expect odd arm positions and should be
  corrected the same way: Guard, Light1–3, Heavy, Jump, QuickStep, HitReaction and
  Death.

---


## 2026-10-22 — Enemy combat animation, Blender pipeline, arm pose

### Enemy combat animation

- `AEnemyBase` had three animation hooks that were empty stubs. `PlayAttackAnimation`
  is called at the start of the attack windup — exactly where a swing belongs,
  because damage lands when that windup expires — so enemies damaged the player
  with no visible attack. It now plays `AM_Hector_Light1` on the shared
  `AB_Hector` (cached once) and warns when the montage cannot be resolved.
- `Die()` already lingered two seconds before `DestroySelf` "to allow death
  animation" but played nothing. It now plays `AM_Hector_Death`, with the same
  missing-asset warning.
- `PlayChaseAnimation` and `PlayIdleAnimation` remain stubs; the locomotion state
  machine covers those cases.

### Blender: store build cannot run scripts

- The Microsoft Store Blender (`WindowsApps\BlenderFoundation.Blender_5.2.2...`)
  cannot be invoked from a shell: `Access is denied`, because Windows ACL-locks
  `WindowsApps`, and no App Execution Alias is installed. `blender -b -P` is
  therefore impossible with that package. It was uninstalled.
- A standalone Blender **4.5.13 LTS** was found at
  `C:\Tools\Blender\blender-4.5.13-windows-x64\blender.exe` and is what the
  pipeline now uses. 4.5 is the safer target for these scripts than 5.x.
- `BuildScripts/regenerate_hector_art.ps1` regenerates the 13 FBX and reports
  which files changed. It auto-discovers Blender on PATH and in the usual install
  roots.
- Note: `Start-Process -ArgumentList` does not quote paths, so a Blender path
  containing spaces was split at the first space and the script reported "Blender
  not found". The path must be passed pre-quoted.

### Arm pose axis (two iterations, second unverified at time of writing)

- `hector_anims.py` dropped the arms with a **Z** rotation. With the arm bone
  running along its own X, Z sweeps the arm horizontally forward — which is the
  "arms out in front" that shipped. Changed to **Y**, the axis that lowers the arm.
- First iteration used 62 degrees. Playtest confirmed the axis was now right
  (arms moved up/down instead of forward) but the arms still did not rest at the
  sides: 62 degrees from a horizontal T-pose leaves them about 28 degrees off
  vertical. Raised to **80 degrees**, and the walk/run cycle arms were converted
  to the same convention (drop on Y, swing on Z) so the idle and walk poses agree.
- No specification documents the rig's bone axes — `AnimationSpec` covers states
  and combat timings, `AnimationFrameData` covers frame counts, notifies and
  retargeting. That omission is why the error was not caught by review.

### Level lighting

- Running the content build without the art pass afterwards leaves the map with
  unbuilt lighting (observed again as "LIGHTING NEEDS TO BE REBUILT (19K unbuilt
  objects)" and a blown-out white scene), because the build regenerates lights as
  static. The quality gate already orders art pass after content build; manual
  content builds must do the same.

### Documentation and repository

- `CHANGELOG.md` and `README.md` now exist in the working project as well as in
  `UE5_Source 5.8/`, so changes are recorded where the code is edited rather than
  only in the published tree.
- Repository audit: `Source/` had 62 files locally but only 14 committed — 21
  `.cpp`, 23 `.h`, 4 `.cs` were missing and a clone could not have compiled. All
  committed in `f949790`.
- 53 generated art files (PBR texture set and Blender previews, 6.35 MB) were
  excluded by a recomp-era blanket `*.png` rule. Committed in `1fd90ef`; the
  negation must be scoped `!UE5_Source 5.8/ArtSource/**/*.png`.
- All PS2 recompilation material was removed or separated: recomp changelog and
  README content moved into rebuild-specific files, then `src/`, `tests/`,
  `tools/`, `patches/`, `release/`, `docs/`, `CMakeLists.txt`, the recomp config
  TOMLs and `BUILDING.md` were deleted (`50668d1`). Everything remains in git
  history.

### Verified state

- Quality gate PASS after the enemy animation changes: C++ build, content build,
  art pass, content QA, substance, gameplay debug (58 checks), F2, F3, F4,
  Chapter 1 acceptance, in-game smoke.
- Content build after the FBX regeneration logged
  `Hector state machine: 17 states, 15 transitions, compiled=True, pose_driven=True`.

---


## UE5 Chapter 1 playable rebuild â€” 2026-10-21

Work on the Unreal Engine 5 rebuild in `UE5_Source 5.8`. Everything below was
verified either by the quality gate or by a live playtest.

### Animation pipeline

- **Root cause of the T-pose and frozen legs**: the generated anim graph wired
  `Root <- Slot <- (empty) SequencePlayer` and left the state machine dangling.
  Montages override the Slot, which is why attacks animated while walking, idling
  and every enemy stayed on the reference pose. The graph now reads
  `Slot [Source <- AnimGraphNode_StateMachine]`, and the content build performs
  that connection itself so a rebuild cannot silently reintroduce the defect.
- Added `ConnectStateMachineToSlot`, `IsStateMachineConnected`, `DumpAnimGraph`,
  `EnsureStateOutputConnected`, `SetEntryStateByName`, `IsEntryConnected` and
  `GetStateSequenceName` to the editor authoring module. `DumpAnimGraph` is what
  exposed the orphaned machine.
- Added `AnimVariableBridge`, which writes `bIsMoving` / `bIsRunning` / `bIsIdle`
  from C++ each tick because `AB_Hector` has no event graph to set them. Wired
  into both `AHectorCharacter` and `AEnemyBase`; missing variables log a warning
  instead of failing silently. Confirmed by playtest: Hector walks, enemies
  animate.

### Enemies

- Enemies were invisible capsules: `EnemyBase` never created a mesh and no mesh
  asset was ever assigned. The art pass now assigns `SK_Hector` to `BP_Skeleton`,
  `BP_Zombie`, `BP_Ghoul` and `BP_SentinelKnight` as a tinted placeholder.
- Enemies now receive `AB_Hector` (previously assigned from a path that did not
  exist, which failed silently) and their locomotion bools are driven.

### Camera and input

- The dormant mode camera called `SetWorldLocationAndRotation` on the spring
  arm's `FollowCamera` every frame, snapping the view back toward the character
  and producing the reported stutter. Its tick is disabled and it returns early
  unless active; camera modes now drive the spring arm instead.
- `PlayerStart` moved from y=-700 to y=-400: the 400-unit boom placed the camera
  exactly on the south wall plane, so playtests began inside a wall.
- Spring arm collision probe disabled with a +70 socket offset so the camera
  cannot be pinned inside blockout geometry.
- Attack hit traces now use `GetBaseAimRotation()` rather than the actor forward
  vector; `bOrientRotationToMovement` only turns the actor while moving, so
  attacking from a standstill used to swing at the wrong direction and miss.
- `PlayerInput` look deltas are consumed each tick; unreleased axes are cleared on
  Completed/Canceled so a released key no longer walks the character forever.

### Level and rendering

- Levels are authored from a commandlet, so Build Lighting and Build Paths never
  ran: Chapter 1 reported 713 unbuilt light interactions and an unbuilt navmesh.
  Lights are now movable with no precomputed lighting, and the navmesh generates
  at runtime via `DefaultEngine.ini`.
- Materials are retinted in place by writing their named parameters and
  recompiling. The previous delete-and-recreate approach silently never ran
  because `does_asset_exist()` reads an asset registry that is not populated at
  commandlet start, which is why Hector stayed a black silhouette for two
  attempts.

### Verification

- Added `Tools/debug_full.py`, a 58-check gameplay audit wired into
  `run_quality_gate.ps1` as its own step: enemy mesh/anim-class/health, Hector's
  mesh, anim class and every input action, skeletal-mesh material flags, room
  spawn tables and trigger sizes, encounter totals, and (new) whether the anim
  graph's state machine actually drives the pose.
- Added `UNobleInputBuilder::GetMappingCount` / `GetMappedActionNames`. `Mappings`
  is protected and Python's `get_mappings()` returns an empty array in this build,
  so the audit previously reported 0 mappings for a context that demonstrably
  drove the game.
- Quality gate: PASS (C++ build, content build, art pass, content QA, substance,
  gameplay debug, F2, F3, F4, Chapter 1 acceptance, in-game smoke).

### Known open items

- **Arms held out in front on both rigs** — RESOLVED 2026-10-22 (see the entry
  above): the drop had to be a local-X rotation, not Z or Y. `hector_anims.py` is
  corrected and the FBX regenerated.
- Enemy animation reuses Hector's clips and mesh; dedicated enemy art is missing.
- F4 asset coverage is 26/75, with 0/49 presentation assets (audio, VFX, UI).
- Four attack clips drift from the 60 fps frame data (F2 reports clip_drift=4).

---

