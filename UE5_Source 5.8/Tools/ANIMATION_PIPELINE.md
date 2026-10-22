# Animation pipeline — current state

Written after a long debugging session in which several confident conclusions
turned out to be wrong. The notes below record what is actually verified.

## Always verify motion before wiring anything

A clip can have the correct skeleton, the correct length, hundreds of tracks and
keys, be bound to the right montage slot, sit in a state machine that is verified
connected, and still be a **static pose**. Structural checks pass for a frozen
clip, so they cannot tell you whether a character will animate.

```
python Tools/probe_clip_moves.py      # samples bones at two frames, compares numbers
python Tools/probe_ac_range.py        # finds where inside a clip the motion sits
```

Two traps this probe itself fell into, worth not repeating:

- comparing `repr()` of a Transform compares the object's memory address, so two
  identical poses read as "different"
- comparing two identical *exception strings* reads as "identical", so a failed
  sample looks like a static clip

Compare the numeric components, and surface sampling errors as errors.

## Retargeting is currently broken

`IKRetargetBatchOperation.duplicate_and_retarget` completes, reports the clips it
created, saves them, and produces **static poses**. Verified: in `RTG_anim_Idle`
every frame holds the same values, and Idle and Walk share byte-identical poses —
the retargeter emits the target's bind pose and never samples the source
animation.

Everything in `Content/Characters/HectorBase/Retargeted` (19 clips) is therefore
unusable. Montages and state machines were built on top of them before this was
noticed, which is why several rounds of "fixes" changed nothing on screen.

Likely cause, not yet confirmed: the retargeter is created from script
(`IKRetargetFactory`) and may have an empty op stack, so no FK-chain retarget op
runs. Worth checking `IKRetargeterController`'s op list before attempting any
future retarget.

## Importing animation directly works

`Tools/import_actorcore.py` imports ActorCore FBXs straight onto
`survival_character_Skeleton` and produces clips that genuinely move. Reallusion
exports in Unreal mode already carry UE bone names (26/26 of the mannequin names
present) plus an explicit UE5 reference pose, so no retarget hop is needed.

One catch, now solved: the imported clips report **900 frames** because the FBX
also contains a 900-frame reference-pose action, so the motion occupies the
opening frames and the rest is padding. Clips must be trimmed first, or they
animate briefly and then hold still.

## Trimming ActorCore motions

`Tools/blender_trim_motion.py` removes the reference action and exports a
motion-only FBX:

```
blender -b --factory-startup -P Tools/blender_trim_motion.py -- <in.fbx> <out.fbx>
```

Two things it must do, each of which silently produced a static clip when missing:

**Assign the action slot.** Blender 4.4+ stores animation per action slot.
Setting `animation_data.action` alone leaves it inert — the armature keeps
evaluating whatever was bound before, which is the reference pose, so the export
bakes a static clip while reporting the correct action name and frame range.

```python
target.animation_data.action = keep
target.animation_data.action_slot = keep.slots[0]
```

**Strip the `cc_base_*` helper bones.** The CC3+ rig has 47 twist and share bones
the character's skeleton lacks. Their curves make UE abort the entire import with
*"Unable to retrieve bone index for track: cc_base_..."*. Only some clips trip
this, because walking animates the leg twist bones and idling does not.

The script verifies its own output: it re-imports the exported FBX into a cleared
scene and samples bones, printing `VERDICT: the exported file animates` or a
warning not to import it.

## Sampling two frames is not enough

A walk cycle returns to the same phase at its midpoint, so sampling only start and
midpoint reads as static for a perfectly good clip. Sample **at least five points**
across the clip, and treat a sampling error as an error rather than as data.

## Talking to the editor

`Tools/mcp_call.py` drives the UnrealMCP plugin over TCP 127.0.0.1:55557 with raw
UTF-8 JSON (`{"type": cmd, "params": {...}}`, no length prefix). The editor must
be running with `Plugins/UnrealMCP` loaded.

Calls must be **strictly sequential** — each command spawns an FTSTicker callback
and overlapping callbacks crash the engine.

Shell notes: PowerShell treats Python's stderr as a fatal error, and
`Start-Process -ArgumentList` does not quote, so scripts here take no arguments
and write results to files in `%TEMP%`.

## Editor-side C++ helpers

`NobleAnimGraphAuthoring` (existing, extended)

- `EnsureSlotNode` / `GetSlotName` / `EnsureSlotPipeline` — a factory-made
  AnimBlueprint has no Slot node, so `ConnectStateMachineToSlot` finds nothing and
  returns false, leaving the machine wired straight to the Root. Montages override
  a slot, not the Root, so attacks would never appear.
- `SetStateSequence` — `AddState` returns an existing state unchanged, so pointing
  a state at a different clip needs this.

`NobleDataTableAuthoring` (new)

- `SetWeaponRowMontages` / `DescribeWeaponRowMontages` / `GetRowNames` — edits
  `FWeaponData`'s two montage arrays in place. Refilling the whole table through
  JSON would require reproducing the pipeline's CSV conversion, and any field it
  fails to reproduce is silently reset to its default.

## Open items

- `Content/Characters/HectorBase/AB_HectorBase` is a stale duplicate that could
  not be deleted from a commandlet (`delete_asset` never flushed, so
  `create_asset` refused the path). The live blueprint is `AB_HectorBaseV2`.
  Clean the stale one up from the editor.
- The 19 static clips under `Retargeted/` should be deleted once the ActorCore
  clips are proven in game.
- `Content/FreeAnimationLibrary/Animations/Idle` contains stray leftovers from
  probe runs (`NewAnimBlueprint`, `RTG_NewRetargeter`, `RTG_NewRetargeter1`).
- The nine `AM_HectorBase_*` montages are bound to the correct skeleton but were
  built from static clips, so they need rebuilding from working clips.
