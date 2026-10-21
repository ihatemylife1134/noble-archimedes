# Changelog - UE5 Chapter 1 rebuild


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

- **Arms held out in front on both rigs.** `hector_anims.py` drops the arms with a
  Z rotation, but with the arm bone running along its own X, Z sweeps horizontally
  forward; Y is the axis that lowers the arm. The source is corrected but the FBX
  has not been regenerated, which requires Blender (not installed).
  `BuildScripts/regenerate_hector_art.ps1` automates the regeneration once it is.
- Enemy animation reuses Hector's clips and mesh; dedicated enemy art is missing.
- F4 asset coverage is 26/75, with 0/49 presentation assets (audio, VFX, UI).
- Four attack clips drift from the 60 fps frame data (F2 reports clip_drift=4).

---

