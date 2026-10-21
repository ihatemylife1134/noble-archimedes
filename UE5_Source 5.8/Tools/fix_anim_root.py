#!/usr/bin/env python3
"""Connect AB_Hector's state machine output to the anim graph Root node.

The state machine was authored correctly but never linked to Root, so its pose
was discarded and the mesh held the reference pose. Idempotent: reports whether
the connection already existed, makes it if not, then recompiles.
"""
import unreal

ANIM_BP = "/Game/Characters/Hector/AB_Hector"

bp = unreal.EditorAssetLibrary.load_asset(ANIM_BP)
if not bp:
    unreal.log_error("[NA-ANIMROOT] AB_Hector not found")
else:
    already = unreal.NobleAnimGraphAuthoring.is_root_connected(bp)
    unreal.log("[NA-ANIMROOT] root connected before: %s" % already)
    unreal.NobleAnimGraphAuthoring.dump_anim_graph(bp)

    machine = unreal.NobleAnimGraphAuthoring.get_or_create_state_machine(bp, "Locomotion")
    if not machine:
        unreal.log_error("[NA-ANIMROOT] no state machine")
    else:
        states = unreal.NobleAnimGraphAuthoring.get_state_names(machine)
        transitions = unreal.NobleAnimGraphAuthoring.get_transition_count(machine)
        unreal.log("[NA-ANIMROOT] machine states=%d transitions=%d" % (len(states), transitions))

        entry = unreal.NobleAnimGraphAuthoring.is_entry_connected(machine)
        unreal.log("[NA-ANIMROOT] entry connected before: %s" % entry)

        for state in states:
            clip = unreal.NobleAnimGraphAuthoring.get_state_sequence_name(machine, state)
            wired = unreal.NobleAnimGraphAuthoring.ensure_state_output_connected(machine, state)
            unreal.log("[NA-ANIMROOT]   state %-14s clip=%-22s output=%s"
                       % (state, clip or "NONE", "OK" if wired else "BROKEN"))

        if not entry:
            ok = unreal.NobleAnimGraphAuthoring.set_entry_state_by_name(machine, "Idle")
            unreal.log("[NA-ANIMROOT] set entry to Idle: %s" % ok)

        if not unreal.NobleAnimGraphAuthoring.is_state_machine_connected(bp):
            ok = unreal.NobleAnimGraphAuthoring.connect_state_machine_to_slot(bp, machine)
            unreal.log("[NA-ANIMROOT] machine->slot connect: %s" % ok)

        unreal.NobleAnimGraphAuthoring.compile_anim_blueprint(bp)
        now = unreal.NobleAnimGraphAuthoring.is_state_machine_connected(bp)
        unreal.EditorAssetLibrary.save_asset(ANIM_BP, only_if_is_dirty=False)
        unreal.log("[NA-ANIMROOT] state machine drives pose: %s" % now)
        unreal.NobleAnimGraphAuthoring.dump_anim_graph(bp)
        unreal.log("[NA-ANIMROOT] RESULT=%s" % ("PASS" if now else "FAIL"))
