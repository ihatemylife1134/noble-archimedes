"""Inspect and repair AB_HectorBaseV2's pose path.

The runtime log shows the anim instance exists and the mesh is in
AnimationBlueprint mode, so the clips are not the problem -- the graph's pose
path is. Three things can silently produce a reference pose while every check
looks green:

  - a state whose sequence player is not linked to its state-result node
  - the state machine not feeding the slot
  - the slot not feeding the root

Every repair call here is idempotent, so this both diagnoses and fixes.
"""
import os

import unreal

OUT = r"C:\Users\Madi\AppData\Local\Temp\fix_pose_path.txt"
ABP = "/Game/Characters/HectorBase/AB_HectorBaseV2"
lines = []


def say(m):
    lines.append(str(m))


try:
    abp = unreal.EditorAssetLibrary.load_asset(ABP)
    say("abp = %s" % abp)

    sm = unreal.NobleAnimGraphAuthoring.get_or_create_state_machine(abp, "Locomotion")
    states = unreal.NobleAnimGraphAuthoring.get_state_names(sm)
    say("states = %s" % states)
    say("entry connected = %s" % unreal.NobleAnimGraphAuthoring.is_entry_connected(sm))
    say("slot name       = %s" % unreal.NobleAnimGraphAuthoring.get_slot_name(abp))
    say("root connected  = %s" % unreal.NobleAnimGraphAuthoring.is_root_connected(abp))
    say("machine in pose = %s" % unreal.NobleAnimGraphAuthoring.is_state_machine_connected(abp))

    say("")
    say("--- state clips ---")
    for state in states:
        say("  %-6s -> %s" % (state, unreal.NobleAnimGraphAuthoring.get_state_sequence_name(sm, state)))

    say("")
    say("--- repair (idempotent) ---")
    for state in states:
        say("  ensure_state_output_connected(%s) = %s" % (
            state, unreal.NobleAnimGraphAuthoring.ensure_state_output_connected(sm, state)))
    say("  ensure_slot_pipeline = %s" % unreal.NobleAnimGraphAuthoring.ensure_slot_pipeline(
        abp, sm, unreal.Name("DefaultSlot")))

    say("")
    say("--- after ---")
    say("  root connected  = %s" % unreal.NobleAnimGraphAuthoring.is_root_connected(abp))
    say("  machine in pose = %s" % unreal.NobleAnimGraphAuthoring.is_state_machine_connected(abp))
    say("  compiled        = %s" % unreal.NobleAnimGraphAuthoring.compile_anim_blueprint(abp))
    say("  saved           = %s" % unreal.EditorAssetLibrary.save_asset(
        ABP, only_if_is_dirty=False))
except Exception as exc:
    say("FAILED: %s" % exc)

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
unreal.log("[NA-FIXPOSE] wrote %d lines" % len(lines))
