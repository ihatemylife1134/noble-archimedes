# Changelog - UE5 Chapter 1 rebuild


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

